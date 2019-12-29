# Item-Catalog
Create a item catalog app where users can add, edit, and delete categories and items in the Category.
## Setup and run the project
### Prerequisites
* Python 3.7
* Vagrant
* VirtualBox

### How to Run
1. Install VirtualBox and Vagrant
2. Clone this repo
3. Unzip and place the Item Catalog folder in your Vagrant directory
4. Launch Vagrant
```
$ Vagrant up 
```
5. Login to Vagrant
```
$ Vagrant ssh
```
6. Change directory to `/vagrant`
```
$ Cd /vagrant
```
7. Initialize the database
```
$ Python itemCatalogDataSetup.py
```
8. Populate the database with some initial data
```
$ Python seedCategoryItems.py
```
9. Launch application
```
$ Python webServer.py
```
10. Open the browser and go to http://localhost:5000

### JSON endpoints
#### Returns JSON of all categories

```
/categories/JSON
```

