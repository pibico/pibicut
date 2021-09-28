## Pibicut

PibiCut is a very Simple Frappe App to produce Shorten URLs on a Frappe Server and at the same time a QR Code to the short URL.

## License

MIT# PibiCut

## Requirements
Requires a Frappe server instance (refer to https://github.com/frappe/frappe), and has dependencies on QR Code (refer to https://github.com/lincolnloop/python-qrcode).

## Compatibility
PibiCut has been tested on Frappe/ERPNext version-12 and version-13 as well.

## Installation
From the frappe-bench folder, execute
```
$ bench get-app pibicut https://github.com/pibico/pibicut.git
$ bench install-app pibicut
```
If you are using a multi-tenant environment, use the following command
```
$ bench --site site_name install-app pibicut
```

## Update
Run updates with
```
$ bench update
```
In case you update from the sources and observe errors, make sure to update dependencies with
```
$ bench update --requirements
```

## Features
Once installed, a new doctype 'Shortener' is generated. On searching the 'Shortener' Doctype you'll enter into the list of created shorten urls. You can create a new one, just click on New and enter the destination long URL. If you want, you can also insert a centered picture on the QR Code (the image must be in PNG format and white background, not transparent).

As a result of saving the 'Shortener' Doctype, you will have a shorten url in the way http or https://site_name/MnOpQ. If you browse to this short url you will be redirected to the long url, the same is produced if you read the generated QR Code. Just try reading the QR Code in the following picture.

![imagen](https://user-images.githubusercontent.com/69711454/135119978-16015a88-b759-4848-8f58-eda8b05bd4cc.png)

## Future Development
Future improvements can be related to QR Code variations taking into consideration the libraries possibilities. Current Generated Short URL is considering random strings with 5 characters, but this can be changed directly in the code. Enjoy this very simple app! 

