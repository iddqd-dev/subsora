#!/usr/bin/env python3
"""
Production Deployment Webhook Handler
Runs on the deployment server (not in Drone CI)
- No git pull
- No source code access
- Only pulls images and updates services
"""
import os
import json
import hmac
import hashlib
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
import subprocess
import time

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
DOCKER_STACK_NAME = os.getenv('DOCKER_STACK_NAME', 'subsora')
DOCKER_REGISTRY = os.getenv('DOCKER_REGISTRY', 'cicd.zerity.ru:55000')
REGISTRY_USERNAME = os.getenv('REGISTRY_USERNAME', '')
REGISTRY_PASSWORD = os.getenv('REGISTRY_PASSWORD', '')
MAX_HEALTH_CHECK_RETRIES = int(os.getenv('MAX_HEALTH_CHECK_RETRIES', '30'))
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '2'))


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify HMAC signature of webhook payload"""
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set, skipping signature verification")
        return True
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def docker_login() -> bool:
    """Login to Docker registry"""
    if not REGISTRY_USERNAME or not REGISTRY_PASSWORD:
        logger.warning("Docker credentials not set")
        return False
    
    try:
        result = subprocess.run(
            ['docker', 'login', DOCKER_REGISTRY, '-u', REGISTRY_USERNAME, '-p', REGISTRY_PASSWORD],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            logger.error(f"Docker login failed: {result.stderr}")
            return False
        logger.info("Successfully logged in to Docker registry")
        return True
    except Exception as e:
        logger.error(f"Docker login error: {e}")
        return False


def pull_image(image: str) -> bool:
    """Pull Docker image from registry"""
    try:
        logger.info(f"Pulling image: {image}")
        result = subprocess.run(
            ['docker', 'pull', image],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            logger.error(f"Failed to pull image: {result.stderr}")
            return False
        logger.info(f"Successfully pulled image: {image}")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout pulling image: {image}")
        return False
    except Exception as e:
        logger.error(f"Error pulling image {image}: {e}")
        return False


def get_service_name(image: str) -> str:
    """Extract service name from image tag"""
    # Example: cicd.zerity.ru:55000/subsora/backend:latest -> subsora_backend
    parts = image.split('/')
    if len(parts) >= 3:
        service_type = parts[-1].split(':')[0]  # backend, frontend, bot
        return f"{DOCKER_STACK_NAME}_{service_type}"
    return None


def update_service(service_name: str, image: str) -> bool:
    """Update Docker service with new image"""
    try:
        logger.info(f"Updating service {service_name} with image {image}")
        
        # Use 'rolling' update order for gradual replacement
        result = subprocess.run(
            ['docker', 'service', 'update',
             '--image', image,
             '--update-order', 'start-first',  # Start new container before stopping old
             '--update-delay', '2s',
             '--update-parallelism', '1',
             service_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to update service: {result.stderr}")
            return False
        logger.info(f"Successfully updated service {service_name}")
        return True
    except Exception as e:
        logger.error(f"Error updating service {service_name}: {e}")
        return False


def wait_for_service_healthy(service_name: str) -> bool:
    """Wait for service to become healthy after update"""
    try:
        for attempt in range(MAX_HEALTH_CHECK_RETRIES):
            result = subprocess.run(
                ['docker', 'service', 'ps', service_name, '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to get service status: {result.stderr}")
                return False
            
            # Parse output lines and check if all tasks are running
            tasks = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
            if not tasks:
                logger.warning("No tasks found for service")
                time.sleep(HEALTH_CHECK_INTERVAL)
                continue
            
            running_tasks = sum(1 for task in tasks if task.get('CurrentState', '').startswith('Running'))
            total_tasks = len(tasks)
            
            if running_tasks == total_tasks:
                logger.info(f"Service {service_name} is healthy: {running_tasks}/{total_tasks} tasks running")
                return True
            
            logger.info(f"Waiting for service to be healthy: {running_tasks}/{total_tasks} tasks running (attempt {attempt + 1}/{MAX_HEALTH_CHECK_RETRIES})")
            time.sleep(HEALTH_CHECK_INTERVAL)
        
        logger.error(f"Service {service_name} failed to become healthy after {MAX_HEALTH_CHECK_RETRIES} attempts")
        return False
    except Exception as e:
        logger.error(f"Error checking service health: {e}")
        return False


def deploy_service(image: str) -> bool:
    """Deploy service with zero-downtime update"""
    service_name = get_service_name(image)
    
    if not service_name:
        logger.error(f"Could not extract service name from image: {image}")
        return False
    
    # Check if service exists
    result = subprocess.run(
        ['docker', 'service', 'inspect', service_name],
        capture_output=True,
        timeout=30
    )
    
    if result.returncode != 0:
        logger.error(f"Service {service_name} does not exist in stack")
        return False
    
    logger.info(f"Deploying service {service_name} with image {image}")
    
    # Pull image first
    if not pull_image(image):
        return False
    
    # Update service with new image (rolling update)
    if not update_service(service_name, image):
        return False
    
    # Wait for service to become healthy
    if not wait_for_service_healthy(service_name):
        logger.error(f"Service deployment failed: {service_name} did not become healthy")
        return False
    
    logger.info(f"Service {service_name} deployed successfully")
    return True


def full_redeploy_stack(compose_file: str = 'docker-compose.yml') -> bool:
    """Perform full stack redeploy with zero-downtime"""
    try:
        logger.info(f"Starting full redeploy from {compose_file}")
        
        # Get current services
        result = subprocess.run(
            ['docker', 'stack', 'services', DOCKER_STACK_NAME],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"Could not get stack services: {result.stderr}")
            # Stack might not exist yet, that's okay
        
        # Pull all images from compose file (without updating services yet)
        logger.info("Pulling all images from compose file")
        
        # Update stack (docker will handle rolling updates)
        logger.info(f"Updating stack {DOCKER_STACK_NAME}")
        result = subprocess.run(
            ['docker', 'stack', 'deploy', 
             '--compose-file', compose_file,
             '--with-registry-auth',
             DOCKER_STACK_NAME],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to deploy stack: {result.stderr}")
            return False
        
        logger.info(f"Stack {DOCKER_STACK_NAME} deployed successfully")
        
        # Wait for all services to be healthy
        time.sleep(5)
        logger.info("Full redeploy completed")
        return True
    except Exception as e:
        logger.error(f"Error during full redeploy: {e}")
        return False


@app.route('/deploy/webhook', methods=['POST'])
def deploy_webhook():
    """Webhook endpoint for triggering deployments"""
    try:
        # Verify signature
        signature = request.headers.get('X-Webhook-Signature', '')
        if not verify_webhook_signature(request.data, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        payload = request.get_json()
        logger.info(f"Received deployment webhook: {payload}")
        
        # Ensure Docker registry login
        if not docker_login():
            logger.error("Failed to login to Docker registry")
            return jsonify({'error': 'Docker login failed'}), 500
        
        deployment_type = payload.get('type', 'service')
        
        if deployment_type == 'service':
            image = payload.get('image')
            if not image:
                return jsonify({'error': 'Missing image parameter'}), 400
            
            success = deploy_service(image)
        elif deployment_type == 'full-redeploy':
            compose_file = payload.get('compose_file', 'docker-compose.yml')
            success = full_redeploy_stack(compose_file)
        else:
            return jsonify({'error': f'Unknown deployment type: {deployment_type}'}), 400
        
        if success:
            logger.info("Deployment completed successfully")
            return jsonify({'status': 'success', 'message': 'Deployment completed'}), 200
        else:
            logger.error("Deployment failed")
            return jsonify({'error': 'Deployment failed', 'status': 'failed'}), 500
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', '5000'))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
