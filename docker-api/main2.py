import docker
from flask import Flask, request, jsonify

app = Flask(__name__)
client = docker.DockerClient(base_url='tcp://machine1:2375')
# instances = {
#     'machine1': {'base_url': 'tcp://machine1:2375'},
#     'machine2': {'base_url': 'tcp://machine2:2375'},
# }
clients = {}
for instance_name, config in instances.items():
    client = DockerClient(base_url=config['base_url'])
    clients[instance_name] = client
    for machine in client:
        create_container("nginx", "nginx", machine)

for instance_name, client in clients.items():
    containers = client.containers.list()
    print(f"Containers on {instance_name}:")
    for container in containers:
        print(container.name)
        
def create_container(image_name, container_name, machine, command=None):
    try:
        container = client.containers.run(image_name, name=container_name, detach=True, command=command)
        return container.id[:12]
    except Exception as e:
        return str(e)

@app.route('/create', methods=['POST'])
def create_container_api():
    data = request.get_json()
    image_name = data['image_name']
    container_name = data['container_name']
    command = data.get('command')

    container_id = create_container(image_name, container_name, command)
    if len(container_id) == 12:
        return jsonify({"message": "Container created successfully", "container_id": container_id}), 201
    else:
        return jsonify({"message": "Failed to create container", "error": container_id}), 500

@app.route('/display/<container_id>', methods=['GET'])
def display_container_info_api(container_id):
    try:
        container = client.containers.get(container_id)
        container_info = {
            "Container ID": container.id[:12],
            "Container Name": container.name,
            "Container Status": container.status,
            "Container IP Address": container.attrs["NetworkSettings"]["IPAddress"]
        }
        return jsonify(container_info), 200
    except docker.errors.NotFound:
        return jsonify({"message": "Container not found"}), 404

@app.route('/stop/<container_id>', methods=['POST'])
def stop_container_api(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return jsonify({"message": "Container stopped successfully"}), 200
    except docker.errors.NotFound:
        return jsonify({"message": "Container not found"}), 404

@app.route('/restart/<container_id>', methods=['POST'])
def restart_container_api(container_id):
    try:
        container = client.containers.get(container_id)
        container.restart()
        return jsonify({"message": "Container restarted successfully"}), 200
    except docker.errors.NotFound:
        return jsonify({"message": "Container not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
