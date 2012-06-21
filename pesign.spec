Summary: Signing utility for UEFI binaries
Name: pesign
Version: 0.2
Release: 1%{?dist}
Group: Development/System
License: GPLv2
URL: https://github.com/vathpela/pesign
# there is no tarball at github, of course.  To get this version do:
# git clone https://github.com/vathpela/pesign.git
# git checkout %%{version}
Source: pesign-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: git gnu-efi nspr nspr-devel nss nss-devel nss-util popt-devel
Requires: nspr nss nss-util popt

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q
git init
git config user.email "pesign-owner@fedoraproject.org"
git config user.name "Fedora Ninjas"
git add .
git commit -a -q -m "%{version} baseline."
git am %{patches} </dev/null

%build
make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_libdir}
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} install

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include %{buildroot}/usr/lib64

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README TODO COPYING
%{_bindir}/pesign
%{_sysconfdir}/popt.d/pesign.popt
%attr(0700,root,root) /etc/pki/pesign

%changelog
* Thu Jun 21 2012 Peter Jones <pjones@redhat.com> - 0.2-1
- Fix some rpmlint complaints nirik pointed out
- Add popt-devel build dep

* Fri Jun 15 2012 Peter Jones <pjones@redhat.com> - 0.1-1
- First version of SRPM.

