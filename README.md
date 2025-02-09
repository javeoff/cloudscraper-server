# cloudscraper-proxy
A simple local proxy server, powered by [cloudscraper](https://github.com/VeNoMouS/cloudscraper)
<br></br>

## Example
Before (standard request, contents blocked by cloudflare)
![image](https://github.com/user-attachments/assets/3ce7e244-8084-4e67-a904-e5a18d229899)

After (using the local server, contents can be accessed normally)
![image](https://github.com/user-attachments/assets/1b282213-6646-4011-abf0-5c19dc3de6d7)


## Usage
Replace the requests you'd like to make in your project
```
https://www.google.com
```
with a request to the bypass server
```
localhost:port/api/proxy/https://www.google.com
```
Then start the server so your project can make requests to it
```
python server.py
```
That's it!
<br></br>

## Configuration
Changing the port can be done simply by editing the bottom of the file
```
if __name__ == "__main__":
    print('Starting cloudflare bypass proxy server')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000) # change the port here
```
Feel free to configure flask or other options to suite your needs

## Using Make Commands
The project includes several Make commands to help manage the Docker container:

```bash
# Build the Docker image
make build

# Run the container
make run 

# Build and run in one command
make up

# Stop and remove the container
make clean

# View container logs
make logs

# Restart the container 
make restart

# Check container status
make status
```

You can change the port and container settings by editing the variables at the top of the Makefile.
