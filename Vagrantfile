# -*- mode: ruby -*-
# vi: set ft=ruby :


git_proxy_wrapper = ENV["GIT_PROXY_COMMAND"]
http_proxy = ENV["http_proxy"]
https_proxy = ENV["https_proxy"]
no_proxy = ENV["no_proxy"]


# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/trusty64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # fix slow connection problems
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--nictype1", "virtio"]
  end

  # copy project folder instead of sharing
  # config.vm.synced_folder ".", "/vagrant", type: "rsync" # , rsync__exclude: ".*/"

  if Vagrant.has_plugin?("vagrant-proxyconf")
      if http_proxy != nil
          config.proxy.http = http_proxy
      end
      if https_proxy != nil
          config.proxy.https = https_proxy
      end
      if no_proxy != nil
          config.proxy.no_proxy = no_proxy
      end
  end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    echo Start provisioning
    export DEBIAN_FRONTEND=noninteractive
    set -xe
    # echo | sudo add-apt-repository cloud-archive:mitaka || true
    sudo apt-get update -y
    sudo apt-get upgrade -y --force-yes
    sudo apt-get install -y --force-yes\
        python2.7 python2.7-dev python-pip python3 python3-dev\
        python-setuptools libffi-dev libssl-dev libxml2-dev libxslt1-dev\
        collectd build-essential git python-libvirt
    sudo pip install -U urllib3 pip>=8 setuptools>=24 tox
    echo Provisioned.
  SHELL

end
