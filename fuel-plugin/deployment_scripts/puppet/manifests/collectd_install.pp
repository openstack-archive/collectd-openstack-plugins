if $operatingsystem == 'Ubuntu' {
    exec { "install collectd":
        command => "apt-get install -y collectd",
        path   => "/usr/bin:/usr/sbin:/bin:/sbin";
    }
}
