#!/bin/bash
# @Author: Rafael Direito
# @Date:   2022-10-24 19:20:02
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 17:56:12
#!/bin/bash
set -eou pipefail

# usage: file_env VAR [DEFAULT]
#    ie: file_env 'XYZ_DB_PASSWORD' 'example'
# (will allow for "$XYZ_DB_PASSWORD_FILE" to fill in the value of
#  "$XYZ_DB_PASSWORD" from a file, especially for Docker's secrets feature)
file_env() {
    local var="$1"
    local fileVar="${var}_FILE"
    local def="${2:-}"
    if [[ ${!var:-} && ${!fileVar:-} ]]; then
        echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
        exit 1
    fi
    local val="$def"
    if [[ ${!var:-} ]]; then
        val="${!var}"
    elif [[ ${!fileVar:-} ]]; then
        val="$(< "${!fileVar}")"
    fi

    if [[ -n $val ]]; then
        export "$var"="$val"
    fi

    unset "$fileVar"
}

SYS_PROPS=""

##################
# Add admin user #
##################

file_env 'KEYCLOAK_USER'
file_env 'KEYCLOAK_PASSWORD'

if [[ -n ${KEYCLOAK_USER:-} && -n ${KEYCLOAK_PASSWORD:-} ]]; then
    /opt/jboss/keycloak/bin/add-user-keycloak.sh --user "$KEYCLOAK_USER" --password "$KEYCLOAK_PASSWORD"
fi

############
# Hostname #
############

if [[ -n ${KEYCLOAK_FRONTEND_URL:-} ]]; then
    SYS_PROPS+="-Dkeycloak.frontendUrl=$KEYCLOAK_FRONTEND_URL"
fi

if [[ -n ${KEYCLOAK_HOSTNAME:-} ]]; then
    SYS_PROPS+=" -Dkeycloak.hostname.provider=fixed -Dkeycloak.hostname.fixed.hostname=$KEYCLOAK_HOSTNAME"

    if [[ -n ${KEYCLOAK_HTTP_PORT:-} ]]; then
        SYS_PROPS+=" -Dkeycloak.hostname.fixed.httpPort=$KEYCLOAK_HTTP_PORT"
    fi

    if [[ -n ${KEYCLOAK_HTTPS_PORT:-} ]]; then
        SYS_PROPS+=" -Dkeycloak.hostname.fixed.httpsPort=$KEYCLOAK_HTTPS_PORT"
    fi

    if [[ -n ${KEYCLOAK_ALWAYS_HTTPS:-} ]]; then
            SYS_PROPS+=" -Dkeycloak.hostname.fixed.alwaysHttps=$KEYCLOAK_ALWAYS_HTTPS"
    fi
fi

################
# Realm import #
################

if [[ -n ${KEYCLOAK_IMPORT:-} ]]; then
    SYS_PROPS+=" -Dkeycloak.import=$KEYCLOAK_IMPORT"
fi

########################
# JGroups bind options #
########################

if [[ -z ${BIND:-} ]]; then
    BIND=$(hostname --all-ip-addresses)
fi
if [[ -z ${BIND_OPTS:-} ]]; then
    for BIND_IP in $BIND
    do
        BIND_OPTS+=" -Djboss.bind.address=$BIND_IP -Djboss.bind.address.private=$BIND_IP "
    done
fi
SYS_PROPS+=" $BIND_OPTS"

#########################################
# Expose management console for metrics #
#########################################

if [[ -n ${KEYCLOAK_STATISTICS:-} ]] ; then
    SYS_PROPS+=" -Djboss.bind.address.management=0.0.0.0"
fi

#################
# Configuration #
#################

# If the server configuration parameter is not present, append the HA profile.
if echo "$@" | grep -E -v -- '-c |-c=|--server-config |--server-config='; then
    SYS_PROPS+=" -c=standalone-ha.xml"
fi

# Adding support for JAVA_OPTS_APPEND
sed -i '$a\\n# Append to JAVA_OPTS. Necessary to prevent some values being omitted if JAVA_OPTS is defined directly\nJAVA_OPTS=\"\$JAVA_OPTS \$JAVA_OPTS_APPEND\"' /opt/jboss/keycloak/bin/standalone.conf

############
# DB setup #
############

file_env 'DB_USER'
file_env 'DB_PASSWORD'
# Lower case DB_VENDOR
if [[ -n ${DB_VENDOR:-} ]]; then
  DB_VENDOR=$(echo "$DB_VENDOR" | tr "[:upper:]" "[:lower:]")
fi

# Detect DB vendor from default host names
if [[ -z ${DB_VENDOR:-} ]]; then
    if (getent hosts postgres &>/dev/null); then
        export DB_VENDOR="postgres"
    elif (getent hosts mysql &>/dev/null); then
        export DB_VENDOR="mysql"
    elif (getent hosts mariadb &>/dev/null); then
        export DB_VENDOR="mariadb"
    elif (getent hosts oracle &>/dev/null); then
        export DB_VENDOR="oracle"
    elif (getent hosts mssql &>/dev/null); then
        export DB_VENDOR="mssql"
    elif (getent hosts h2 &>/dev/null); then
        export DB_VENDOR="h2"
        export DB_ADDR="h2"
    fi
fi

# Detect DB vendor from legacy `*_ADDR` environment variables
if [[ -z ${DB_VENDOR:-} ]]; then
    if (printenv | grep '^POSTGRES_ADDR=' &>/dev/null); then
        export DB_VENDOR="postgres"
    elif (printenv | grep '^MYSQL_ADDR=' &>/dev/null); then
        export DB_VENDOR="mysql"
    elif (printenv | grep '^MARIADB_ADDR=' &>/dev/null); then
        export DB_VENDOR="mariadb"
    elif (printenv | grep '^ORACLE_ADDR=' &>/dev/null); then
        export DB_VENDOR="oracle"
    elif (printenv | grep '^MSSQL_ADDR=' &>/dev/null); then
        export DB_VENDOR="mssql"
    elif (printenv | grep '^H2_ADDR=' &>/dev/null); then
        export DB_VENDOR="h2"
        export DB_ADDR="h2"
    fi
fi

# Default to H2 if DB type not detected
if [[ -z ${DB_VENDOR:-} ]]; then
    export DB_VENDOR="h2"
fi

# if the DB_VENDOR is postgres then append port to the DB_ADDR
function append_port_db_addr() {
  local db_host_regex='^[a-zA-Z0-9]([a-zA-Z0-9]|-|.)*:[0-9]{4,5}$'
  IFS=',' read -ra addresses <<< "$DB_ADDR"
  DB_ADDR=""
  for i in "${addresses[@]}"; do
    if [[ $i =~ $db_host_regex ]]; then
        DB_ADDR+=$i;
    else
        DB_ADDR+="${i}:${DB_PORT}";
    fi
    DB_ADDR+=","
  done
  DB_ADDR=$(echo $DB_ADDR | sed 's/.$//') # remove the last comma
}
# Set DB name
case "$DB_VENDOR" in
    postgres)
        DB_NAME="PostgreSQL"
        if [[ -z ${DB_PORT:-} ]] ; then
          DB_PORT="5432"
        fi
        append_port_db_addr
        ;;
    mysql)
        DB_NAME="MySQL";;
    mariadb)
        DB_NAME="MariaDB";;
    mssql)
        DB_NAME="Microsoft SQL Server";;
    oracle)
        DB_NAME="Oracle";;
    h2)
        if [[ -z ${DB_ADDR:-} ]] ; then
          DB_NAME="Embedded H2"
        else
          DB_NAME="H2"
        fi;;
    *)
        echo "Unknown DB vendor $DB_VENDOR"
        exit 1
esac

if [ "$DB_VENDOR" != "mssql" ] && [ "$DB_VENDOR" != "h2" ]; then
    # Append '?' in the beginning of the string if JDBC_PARAMS value isn't empty
    JDBC_PARAMS=$(echo "${JDBC_PARAMS:-}" | sed '/^$/! s/^/?/')
else
    JDBC_PARAMS=${JDBC_PARAMS:-}
fi

export JDBC_PARAMS

# Convert deprecated DB specific variables
function set_legacy_vars() {
  local suffixes=(ADDR DATABASE USER PASSWORD PORT)
  for suffix in "${suffixes[@]}"; do
    local varname="$1_$suffix"
    if [[ -n ${!varname:-} ]]; then
      echo WARNING: "$varname" variable name is DEPRECATED replace with DB_"$suffix"
      export DB_"$suffix=${!varname}"
    fi
  done
}
set_legacy_vars "$(echo "$DB_VENDOR" | tr "[:upper:]" "[:lower:]")"

# Configure DB

echo "========================================================================="
echo ""
echo "  Using $DB_NAME database"
echo ""
echo "========================================================================="
echo ""

configured_file="/opt/jboss/configured"
if [ ! -e "$configured_file" ]; then
    touch "$configured_file"

    if [ "$DB_NAME" != "Embedded H2" ]; then
      /bin/sh /opt/jboss/tools/databases/change-database.sh $DB_VENDOR
    fi
	
    /opt/jboss/tools/x509.sh
    /opt/jboss/tools/jgroups.sh
    /opt/jboss/tools/infinispan.sh
    /opt/jboss/tools/statistics.sh
    /opt/jboss/tools/vault.sh
    /opt/jboss/tools/autorun.sh
fi


######################
# 1st Start Keycloak #
######################

set -m
exec nohup /opt/jboss/keycloak/bin/standalone.sh $SYS_PROPS $@ &



until $(curl --output /dev/null --silent --head --fail http://localhost:8080/auth); do
    printf 'waiting for the service to be alive...'
    sleep 5
done


cd /opt/jboss/keycloak/bin
# Log in
./kcadm.sh config credentials --server http://localhost:8080/auth --realm master --user $KEYCLOAK_USER --password $KEYCLOAK_PASSWORD

REALM_CREATED=0
./kcadm.sh get realms/$MY_REALM_NAME || REALM_CREATED=1

if [ "$REALM_CREATED" -eq 0 ]; then
    echo "Realm $MY_REALM_NAME already exists!"
    pid=$(ps | grep standalone.sh | awk '{print $1}')
    kill $pid

    ######################
    # 2nd Start Keycloak #
    ######################

    exec /opt/jboss/keycloak/bin/standalone.sh $SYS_PROPS $@
    exit $?
fi


# Create Realm
./kcadm.sh create realms -s realm=$MY_REALM_NAME -s enabled=true -o
# Configure Admin
export ADMIN_CLI_ID=$(./kcadm.sh get clients -r $MY_REALM_NAME --fields clientId,id  | jq '.[] | select(.clientId==("admin-cli")) | .id' | tr -d '"')
./kcadm.sh  update clients/$ADMIN_CLI_ID -r $MY_REALM_NAME -s publicClient=false -s secret=$MY_REALM_ADMIN_SECRET -s serviceAccountsEnabled=true  -s authorizationServicesEnabled=true -s fullScopeAllowed=true
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename manage-account
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename delete-account
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename manage-account-links
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename manage-consent
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename view-applications
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename view-consent
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid account --rolename view-profile
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename query-groups
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-clients
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename realm-admin
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-users
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename query-realms
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-events
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-realm
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-clients
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-events
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename create-client
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-identity-providers
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-authorization
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename query-users
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-identity-providers
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename impersonation
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename query-clients
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-authorization
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename manage-realm
./kcadm.sh add-roles -r $MY_REALM_NAME --uusername service-account-admin-cli --cclientid realm-management --rolename view-users
# Configure Custom Client
./kcadm.sh create clients -r $MY_REALM_NAME  -f - << EOF
  {
    "clientId": "$MY_REALM_CLIENT",
    "rootUrl": "",
    "baseUrl": "/",
    "surrogateAuthRequired": false,
    "enabled": true,
    "alwaysDisplayInConsole": false,
    "clientAuthenticatorType": "client-secret",
    "secret": "$MY_REALM_CLIENT_SECRET",
    "webOrigins": ["+"],
    "bearerOnly": false,
    "consentRequired": false,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "publicClient": false,
    "authorizationServicesEnabled": true,
    "frontchannelLogout": false,
    "protocol": "openid-connect",
    "defaultClientScopes": ["web-origins","role_list","roles","profile","email"],
    "optionalClientScopes": ["address","phone","offline_access","microprofile-jwt"],
    "fullScopeAllowed": true,
    "redirectUris": [$MY_REALM_REDIRECT_URI],
    "rootUrl": "",
    "baseUrl": ""
  }
EOF

IFS=";"
read -a roles_info_array <<< "$REALM_ROLES"

for role_info_str in "${roles_info_array[@]}"
do
    IFS=":"
    read -a role_info <<< "$role_info_str"
    role=${role_info[0]}
    description=${role_info[1]}

    
    echo "Adding role: '$role' with description '$description'..."
    # Add role in keycloak
    ./kcadm.sh create roles -r $MY_REALM_NAME -s name=$role -s "description=$description"
    echo "Added role: '$role' with description '$description'."
done

IFS=";"
read -a users_array <<< "$REALM_USERS"
for user in "${users_array[@]}"
do
    IFS=":"
    read -a user_info <<< "$user"

    username=${user_info[0]}
    password=${user_info[1]}
    roles_str=${user_info[2]}

    echo "Adding user '$username'..."
    ./kcadm.sh create users -r $MY_REALM_NAME -s username=$username -s enabled=true
    ./kcadm.sh set-password -r $MY_REALM_NAME --username $username --new-password $password
    echo "Added user '$username'."
    if [[ $roles_str != "None" ]]
    then
        IFS=","
        read -a roles <<< "$roles_str"
        for role in "${roles[@]}"
        do
            echo "Adding role '$role' to user '$username'..."
            ./kcadm.sh add-roles --uusername $username --rolename $role -r $MY_REALM_NAME
            echo "Added role '$role' to user '$username'."
        done
    else
        echo "User '$username' was added without any role."
    fi
done

job_id=$(jobs | grep standalone.sh | awk '{print $1}' | awk '{print substr($0, 2, length($0) - 3)}')
echo "JOB ID: $job_id"
fg % $job_id