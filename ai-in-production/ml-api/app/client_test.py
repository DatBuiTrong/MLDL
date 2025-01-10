import requests
from api.entities.vehicle import Vehicle, VehicleResponse


def send_event(event_endpoint):

    data_event = Vehicle(user_id="user_id", cam_id="cam_id", time="time", metadata="metadata")
    data_event = data_event.dict()
    bytes_image = open("/mnt/data/server_worker/ml-models-in-production/public/people.jpg", "rb")
    file = {"file": ("people.jpg", bytes_image, "image/jpg")}
    event_res = requests.post(event_endpoint,
                              headers={"Content_Type": "Content_Header"},
                              data=data_event,
                              files=file,
                              timeout=5)
    
    print(event_res.json())
    status_code = event_res.status_code

    return status_code

if __name__=="__main__":
    event_endpoint = "http://localhost:8081/api/v1/vehicle/upload_data"
    send_event(event_endpoint=event_endpoint)
