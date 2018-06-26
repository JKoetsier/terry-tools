#!/bin/bash

sudo yum install -y wget
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo rpm -ivh epel-release-latest-7.noarch.rpm
rm epel-release-latest-7.noarch.rpm

sudo yum install -y htop vim unzip

wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u171-b11/512cd62ec5174c3487ac17c61aaa89e8/jdk-8u171-linux-x64.rpm"
sudo yum localinstall jdk-8u171-linux-x64.rpm
rm jdk-8u171-linux-x64.rpm