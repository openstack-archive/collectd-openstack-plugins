local xtrace=$(set +o | grep xtrace)
set -o xtrace

    # Initial source of lib script
    source $COLLECTD_DIR/devstack/libs/collectd

    case $1 in
        "stack")
            case $2 in
                "pre-install")
                    # install system package
                    install_collectd
                ;;
                "install")
                    # adapt collectd.conf
                    adapt_collectd_conf
                ;;
                "post-config")
                    # start collectd service
                    start_collectd
                ;;
                "extra")
                    # no-op
                    :
                ;;
            esac
        ;;
        "unstack")
            #  stop the service and restore original /etc/collect.conf
            stop_collectd
            restore_collectd_conf
        ;;
        "clean")
            # no cleaning required as of now
            :
        ;;
    esac

$xtrace
