Name:		eayunstack-tools
Version:	1.0
Release:	3%{?dist}
Summary:	EayunStack Management tools

Group:		Application
License:	GPL
URL:		https://github.com/eayunstack/eayunstack-tools
Source0:	eayunstack-tools-%{version}.tar.gz

BuildRequires:	/bin/bash
BuildRequires:	python
BuildRequires:	python2-devel
BuildRequires:	python-setuptools
Requires:	python
Requires:	MySQL-python
Requires:	python-paramiko
Requires:	python-fuelclient
Requires:	python-cinder

%description
EayunStack Management Tools

%prep
%setup -q


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python2} setup.py build


%install
rm -rf %{buildroot}
%{__python2} setup.py install --skip-build --root %{buildroot}
mkdir -p %{buildroot}/.eayunstack/
cp -r template %{buildroot}/.eayunstack/

%post
if [ "$1" = "1" ]; then

useradd eayunadm &> /dev/null
passwd -d eayunadm &> /dev/null
passwd -e eayunadm &> /dev/null
echo 'eayunadm	ALL=(ALL)	NOPASSWD:/bin/eayunstack' >> /etc/sudoers

# modify PS1
echo '
# write by eayunstack-tools
if [ -f /.eayunstack/node-role ];then
    noderole=`cat /.eayunstack/node-role`
    export PS1="[\u@\h \W]($noderole)\\$ "
fi

' >> /etc/bashrc
fi

%postun
if [ "$1" = "0" ]; then
    sed -i -e '/^eayunadm/d' /etc/sudoers
fi


%files
%doc
%attr(0755,root,root)/.eayunstack
/usr/bin/eayunstack
/usr/lib/python2.7/site-packages/


%changelog
* Fri May 15 2015 blkart <blkart.org@gmail.com> 1.0-3
- modify spec file

* Mon May 11 2015 blkart <blkart.org@gmail.com> 1.0-2
- commit 8d9af51a016922967814707b540c7523a518ddcd
- modify spec & makefile file

* Thu May 7 2015 blkart <blkart.org@gmail.com> 1.0-1
- commit ed7658fbe90d3165591a02f06bdf9af63091c907
