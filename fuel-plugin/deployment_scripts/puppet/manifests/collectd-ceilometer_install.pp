$master_ip         = hiera('master_ip')
$use_ceilometer    = hiera('use_ceilometer', false)

$management_vip    = hiera('management_vip')
$service_endpoint  = hiera('service_endpoint', $management_vip)
$ssl_hash          = hiera_hash('use_ssl', {})
$auth_protocol     = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'protocol', 'http')
$auth_endpoint     = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'hostname', [$service_endpoint])
$auth_uri          = "${auth_protocol}://${auth_endpoint}:5000/v2.0"

$ceilometer_hash   = hiera_hash('ceilometer', {'user'=>'ceilometer'})
$auth_user         = 'ceilometer'
$auth_password     = $ceilometer_hash['user_password']

$exe_url = "http://${master_ip}:8080/plugins/fuel-plugin-collectd-ceilometer-0.9/deployment_scripts/install.sh"

if ($use_ceilometer) {

    exec { "install collectd-ceilometer":
        command => "curl ${exe_url} | bash -s ${master_ip} ${auth_uri} ${auth_user} ${auth_password}",
        path   => "/usr/bin:/usr/sbin:/bin:/sbin";
    }
}
