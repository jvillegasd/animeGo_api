# animeGo_api
My Restful API for my mobile app animeGo. <br>
This RestFul API web scrapes spanish and english anime sites.
# 1. Running the web app <br>
This web application uses Docker for deployment. There are two containers over the same network. One of them is the Flask Image that is the API. The another one is a Nginx Image configured as a reverse proxy for Flask container deployment. <br>
**Ports 80 and 8080 are required**

## 1.1 Docker commands to API RestFul deployment <br>
```
docker-compose up -d
```
## 1.2 Docker Old Files folder <br>
This folder contains docker files with low size containers. Use it if you do not have to scrape on sites with CloudFlare's IUAM protection. <br>
# 2. API Documentation <br>
The endpoint ```http://{your host ip}/swagger.json``` gives you the documentation. Also, you can read it in ```api_doc.json``` file on this repo.
