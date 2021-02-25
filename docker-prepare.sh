#!/usr/bin/env bash

set -ex
echo "PWD=$PWD"

##################
#                #
#    FRONTEND    #
#                #
##################

if [[ -f "bower.json" ]]; then  # BOWER
    cat > ".bowerrc" <<EOL
{
  "directory": "_project_/static/bower_components/",
  "analytics": false
}
EOL
    mkdir -p _project_/static/bower_components
    chown -R unprivileged:unprivileged _project_/static/bower_components
    gosu unprivileged bower install
fi

if [[ -f "package.json" ]]; then  # NPM
    npm install
fi

if [[ -f "gulpfile.js" ]]; then  # GULP
    gulp
fi

STATIC_ROOT=${STATIC_ROOT:-"`pwd`/__data__/static"}
mkdir -p $STATIC_ROOT
python manage.py collectstatic --noinput
./manage.py collectstatic --noinput
./manage.py generateopenapi --format=openapi-json > ${STATIC_ROOT}/api_schema_openapi-json.txt
./manage.py generateopenapi --format=openapi > ${STATIC_ROOT}/api_schema_openapi.txt
