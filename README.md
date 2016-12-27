# asterix-data

XML description of ASTERIX data format as specified in 
http://www.eurocontrol.int/services/asterix.
Each ASTERIX category and revision is specified in a separate `.xml` file.

## Install

* `scons` utility is used to run validation and installation (similar to `make`).
* `jing` application is used to optionally validate xml file against the template.

### Data validation

To validate XML (not strictly necessary), use:

    scons validate
    
### Installation

To install files to default location `/usr/local/share/asterix-data`, use:

    scons install
    <or>
    sudo scons install
    
To install files to custom location, use for example:

    mkdir tmp
    scons install --prefix=tmp
    
