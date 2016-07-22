# -*- mode: ruby -*-

# Takes proxy configuratiom from host environment
http_proxy = ENV["http_proxy"]
https_proxy = ENV["https_proxy"]
no_proxy = ENV["no_proxy"]
if http_proxy or https_proxy
  require 'vagrant-proxyconf'
end

# This where the working directory is going to be copied/mounted inside of
# produced VM.
source_dir="/vagrant"

# This is the synchronization strategy to copy or mount wirking directory
# inside the VM. For more details read below doc:
#     https://www.vagrantup.com/docs/synced-folders/
sync_type="rsync"

# For the purpose of deplying openstack code inside provisioned VM it is using
# git to fetch source code from upstream. The repository server can be changed
# by setting this variable to point to some other place.
# A common alternative value is "https://github.com"
# This value is taken from host env configuration when available.
# If this value is empty then the default git server knwon by devstak is used
# that in the moment this doc is written is "https://git.openstack.org"
git_base = ENV["GIT_BASE"] or ""

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
  config.vm.box = "ubuntu/xenial64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Collectd will fail to install if it is not able to resolve the ip from its
  # hostname. Setting the host name here will make Vagrant configuring
  # /etc/hosts fixing this problem
  config.vm.hostname = "vagrant"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP. This internal private network will be used by collectd
  config.vm.network "private_network", ip: "192.168.0.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", source_dir, create:true, type: sync_type

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false

    # Customize the amount of memory on the VM. This ammout is recommended
    # to make OpenStack working.
    vb.memory = "2048"
  end

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Fix slow connection problems
  # config.vm.provider "virtualbox" do |v|
  #   v.customize ["modifyvm", :id, "--nictype1", "virtio"]
  # end

  # Configure proxy variables
  if Vagrant.has_plugin?("vagrant-proxyconf")
    if http_proxy
      config.proxy.http = http_proxy
    end
    if https_proxy
      config.proxy.https = https_proxy
    end
    if no_proxy
      config.proxy.no_proxy = no_proxy
    end
  end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # Below script is going to be executed inside of the VM as regular user
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    set -x

    # forward configuration from the hos to the guest VM
    export GIT_BASE="#{git_base}"
    export SOURCE_DIR="#{source_dir}"

    # run provisioning script
    "$SOURCE_DIR"/tools/provision.sh
  SHELL
end
