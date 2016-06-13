exec { "restart collectd":
    command => "service collectd restart",
    path   => "/usr/bin:/usr/sbin:/bin:/sbin";
}
