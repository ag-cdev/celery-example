import docker

def create_container(client, image_name, container_name, command=None):
    container = client.containers.run(image_name, name=container_name, detach=True, command=command)
    print(f"Container {container.id[:12]} created.")
    return container

def display_container_info(container):
    container_info = container.attrs
    print("Container ID:", container_info["Id"])
    print("Container Name:", container_info["Name"])
    print("Container Status:", container_info["State"]["Status"])
    print("Container IP Address:", container_info["NetworkSettings"]["IPAddress"])

def stop_container(container):
    container.stop()
    print("Container stopped.")

def restart_container(container):
    container.restart()
    print("Container restarted.")

def get_docker_client():
    try:
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        return client
    except Exception as e:
        print(f"Error creating Docker client: {e}")
        return None

if __name__ == "__main__":
    client = get_docker_client()

    if client:
        client = docker.from_env()

        image_name = "nginx:latest"
        container_name = "my-nginx-container"

        # Create a container
        container = create_container(client, image_name, container_name)

        # Display container information
        display_container_info(container)

        # Stop the container
        stop_container(container)

        # Restart the container
        restart_container(container)
    else:
        print("Docker client not available.")