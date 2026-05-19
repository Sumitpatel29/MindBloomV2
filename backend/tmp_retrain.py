import requests
url='http://localhost:8000/api/admin/models/retrain'
headers={'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiaWF0IjoxNzc5MDA3ODA4LCJleHAiOjE3Nzk2MTI2MDh9.36oraNjJOhrBPZV4Y-CcIGRoU0VW5zaMzRvepc1N7IE','Content-Type':'application/json'}
json={'model_dir':'backend/ml_models','feature_path':'backend/ml_data/features.parquet','epochs':2,'batch_size':8,'contamination':0.1}
resp=requests.post(url, headers=headers, json=json)
print(resp.status_code)
print(resp.text)
