# truenas-scale-restart-app

This repository builds the `danielriedl/truenas-scale-restart-app` Docker Image.</br>
It can be used to restart TrueNAS Scale Applications from anywhere, as it uses `midclt` from [here](https://github.com/truenas/middleware).

## Getting Started

These instructions will cover usage information and for the docker container

### Prerequisities


In order to run this container you'll need TrueNAS Scale installed.</br>


### Usage

#### Container Parameters


```shell
docker run -it --rm danielriedl/truenas-scale-restart-app -h
usage: app.py [-h] [-s SERVICE_ID] [--start-api | --no-start-api] [-u URI] [-U USERNAME] [-P PASSWORD]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE_ID, --service-id SERVICE_ID
                        The service ID to restart
  --start-api, --no-start-api
  -u URI, --uri URI
  -U USERNAME, --username USERNAME
  -P PASSWORD, --password PASSWORD
```

#### Example to test the connection

```shell
docker run -it --rm danielriedl/truenas-scale-restart-app \
    -s my-scale-app \
    -u ws://10.0.1.6:8080/websocket \
    -U root \
    -P MySecret

INFO:root:Will scale service my-scale-app to 0.
INFO:root:Created scale job 8296
INFO:root:Waiting for Job 8296 to finish
[... SNIP]
INFO:root:Waiting for Job 8296 to finish
INFO:root:Job 8296 succeeded
INFO:root:Will scale service my-scale-app to 1.
INFO:root:Created scale job 8301
INFO:root:Waiting for Job 8301 to finish
INFO:root:Job 8301 succeeded
INFO:root:Guess it worked, as this is the end of the script.
```

#### API
The application offers an Flask API. Start it with:

```shell
docker run -it --rm -p 8080:8080 danielriedl/truenas-scale-restart-app --start-api
```

Do a POST request to `/restart` do the same thing as above:
```json
{
    "uri": "ws://10.0.1.6:8080/websocket",
    "username": "root",
    "password": "MySecret",
    "service_id": "my-scale-app"
}
```

## Setup as TrueNAS Scale App

* Go to `/ui/apps` and click top right on `Launch Docker Image`
* **(1) Application Name** - Set `Application Name` to `restart-app`
* **(2) Container Images** - Set `Image repository` to `danielriedl/truenas-scale-restart-app`
* **(3) Configure Entrypoint** - Set `Configure Container Args` to `--start-api`
* **(6) Port Forwarding** - Add one Rule to forward `Container Port` of `8080` to your desired `Node Port` e.g `10011`
* **(13) Confirm Options** - Click on Save

<ins>Now you can use the API from other TrueNAS Scale apps with following URL:</ins></br>
http://restart-app-ix-chart.ix-restart-app.svc.cluster.local:8080/restart

Or from somewhere else</br>
http://ip-of-system:10011/restart

## But y tho
So I made a mistake and was setting up home-assistant for my dad.</br>
Kind of funny architecture, as I use the wireguard addon of the home-assistant chart to connect to his FritzBox VPN.</br>
As our ISP decides randomly, when to assign new IPv4 Adresses to private households the connection drops from both sides,</br>
resulting in a call from Dad `Dan wtf nothing works`.</br>
So the goal was to restart the whole home-assistant TrueNAS Scale App of his installation, to reconnect everything.</br>
This was approached by a simple node-red flow:</br>
If certain entities are unavailable for 5 minutes trigger the `/restart` API endpoint.</br>

Since then - no calls (atleast those where he's reporting network problems).

## Authors

* **Dan Riedl** - *Initial work* - [danriedl](https://github.com/danriedl)

## Acknowledgments
Everything relys on a [forum thread](https://www.truenas.com/community/threads/chart-application-restart-flow.104390/) I found while searching for solutions.</br>
So kudos to MVP [kiler129](https://www.truenas.com/community/members/kiler129.58953/)
