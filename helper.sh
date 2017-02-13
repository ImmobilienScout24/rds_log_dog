# source this file only

function set_templates_and_stack_names {
   local BASENAME=rds-log-dog
   local POSTFIX=""
   if [ ${PERSONAL_BUILD} == true ]; then
      POSTFIX="-${USER:0:3}"
   fi
   DST_BUCKET_STACK_NAME="${BASENAME}-s3${POSTFIX}"
   FUNCTION_STACK_NAME="${BASENAME}-lambda${POSTFIX}"
   SCHEDULER_STACK_NAME="${BASENAME}-scheduler${POSTFIX}"
}

function set_dst_s3_bucket_name_from_stack {
    S3_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name ${DST_BUCKET_STACK_NAME} | jq -r '.[]|.[].Outputs|.[]|select(.OutputKey=="name")|.OutputValue')
}

function unset_proxy_env {
    for v in $(env |awk -v FS='=' ' {print $1}' | grep -ie '^http.*_proxy$'); do 
        export __$v=$v
        echo "unsetting env: $v"
        unset $v
    done
}

function restore_proxy_env {
    for v in $(env |awk -v FS='=' ' {print $1}' | grep -ie '^__http.*_proxy$'); do 
        export eval "${v:2}=$v"
        unset $v
    done
}

