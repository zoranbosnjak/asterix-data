# asterix-data

XML description of ASTERIX data format as specified in
<http://www.eurocontrol.int/services/asterix>.
Each ASTERIX category and revision is specified in a separate `.xml` file.

**_NOTE:_** This projet is obsolete in favor of
<https://github.com/zoranbosnjak/asterix-specs>.
For the existing projects, it is still possible to use these xml definitions,
but it is important to note, that the definitions are automatically generated
from the upstream `asterix-specs` repository. Do not edit *.xml* files directly.

## Manual specification update procedure

**_NOTE:_** This is normally not necessary. The *.xml* files are updated
periodically from github actions.

```bash
export ASTERIX_SPECS_REV=$(./update-specs.py xml --reference)
echo $ASTERIX_SPECS_REV

git rm xml/*
./update-specs.py xml
git add xml

# review changes
git diff --cached

# commit with reference to asterix-specs revision
git commit -m "Sync with asterix-specs #$ASTERIX_SPECS_REV"
```

# Install

* `scons` utility is used to run validation and installation (similar to `make`).
* `jing` application is used to optionally validate xml file against the template.

## Data validation

To validate XML (not strictly necessary), use:

```bash
scons validate
```

## Installation

To install files to default location `/usr/local/share/asterix-data`, use:

```bash
scons install
# or
sudo scons install
```

To install files to custom location, use for example

```bash
mkdir tmp
scons install --prefix=tmp
```

