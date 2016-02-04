%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

Summary: Signing utility for UEFI binaries
Name: pesign
Version: 0.111
Release: 8%{?dist}
Group: Development/System
License: GPLv2
URL: https://github.com/vathpela/pesign
Obsoletes: pesign-rh-test-certs <= 0.111-7
BuildRequires: git nspr nss nss-util popt-devel
BuildRequires: coolkey opensc nss-tools
BuildRequires: nspr-devel >= 4.9.2-1
BuildRequires: nss-devel >= 3.13.6-1
BuildRequires: efivar-devel >= 0.14-1
BuildRequires: libuuid-devel
BuildRequires: tar xz
Requires: nspr nss nss-util popt rpm coolkey opensc
Requires(pre): shadow-utils
ExclusiveArch: i686 x86_64 ia64 aarch64
%if 0%{?rhel} >= 7
BuildRequires: rh-signing-tools >= 1.20-2
%endif

Source0: https://github.com/vathpela/pesign/releases/download/%{version}/pesign-%{version}.tar.bz2
Source1: certs.tar.xz
Patch0001: 0001-Fix-one-more-Wsign-compare-problem-I-missed.patch
Patch10001: 0001-pesign-when-nss-fails-to-tell-us-EPERM-or-ENOENT-fig.patch
Patch10002: 0002-setfacl-the-nss-DBs-to-our-authorized-users-not-just.patch
Patch10003: 0003-Don-t-setfacl-when-the-socket-or-dir-aren-t-there.patch
Patch10004: 0004-setfacl-the-db-as-well.patch
Patch10005: 0005-Do-a-better-job-of-isolating-pesign-rh-test-crap.patch

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q -a 0 
%setup -a 1 -D -c -n pesign-%{version}/
git init
git config user.email "pesign-owner@fedoraproject.org"
git config user.name "Fedora Ninjas"
git add .
git commit -a -q -m "%{version} baseline."
git am %{patches} </dev/null
git config --unset user.email
git config --unset user.name

%build
make PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_libdir}
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} \
	install
%if 0%{?rhel} >= 7 || 0%{?fedora} >= 17
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} \
	install_systemd
%endif

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*
mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign/
mkdir -p %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/
cp -a etc/pki/pesign/* %{buildroot}%{_sysconfdir}/pki/pesign/
cp -a etc/pki/pesign-rh-test/* %{buildroot}%{_sysconfdir}/pki/pesign-rh-test/

if [ %{macrosdir} != %{_sysconfdir}/rpm ]; then
	mkdir -p %{buildroot}%{macrosdir}
	mv %{buildroot}%{_sysconfdir}/rpm/macros.pesign \
		%{buildroot}%{macrosdir}
	rmdir %{buildroot}%{_sysconfdir}/rpm
fi
rm -f %{buildroot}/usr/usr/share/doc/pesign-0.111/COPYING

%pre
getent group pesign >/dev/null || groupadd -r pesign
getent passwd pesign >/dev/null || \
	useradd -r -g pesign -d /var/run/pesign -s /sbin/nologin \
		-c "Group for the pesign signing daemon" pesign
exit 0

%if 0%{?rhel} >= 7 || 0%{?fedora} >= 17
%post
%systemd_post pesign.service
modutil -force -dbdir %{_sysconfdir}/pki/pesign -add opensc \
	-libfile %{_libdir}/pkcs11/opensc-pkcs11.so >/dev/null
#modutil -force -dbdir %{_sysconfdir}/pki/pesign -add coolkey \
#	-libfile %%{_libdir}/pkcs11/libcoolkeypk11.so
%preun
%systemd_preun pesign.service

%postun
%systemd_postun_with_restart pesign.service
%else
%post
modutil -force -dbdir %{_sysconfdir}/pki/pesign -add opensc \
	-libfile %{_libdir}/pkcs11/opensc-pkcs11.so >/dev/null
%endif

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc README TODO
%{_bindir}/authvar
%{_bindir}/efikeygen
%{_bindir}/efisiglist
%{_bindir}/pesigcheck
%{_bindir}/pesign
%{_bindir}/pesign-client
%dir %{_libexecdir}/pesign/
%dir %attr(0770,pesign,pesign) %{_sysconfdir}/pki/pesign/
%attr(0660,pesign,pesign) %{_sysconfdir}/pki/pesign/*
%dir %attr(0775,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/
%attr(0664,pesign,pesign) %{_sysconfdir}/pki/pesign-rh-test/*
%{_libexecdir}/pesign/pesign-authorize-users
%{_libexecdir}/pesign/pesign-authorize-groups
%config(noreplace)/%{_sysconfdir}/pesign/users
%config(noreplace)/%{_sysconfdir}/pesign/groups
%{_sysconfdir}/popt.d/pesign.popt
%{macrosdir}/macros.pesign
%{_mandir}/man*/*
%dir %attr(0770,pesign,pesign) %{_sysconfdir}/pki/pesign
%attr(0660,pesign,pesign) %{_sysconfdir}/pki/pesign/*
%dir %attr(0770, pesign, pesign) %{_localstatedir}/run/%{name}
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/socket
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/pesign.pid
%if 0%{?rhel} >= 7 || 0%{?fedora} >= 17
%{_tmpfilesdir}/pesign.conf
%{_unitdir}/pesign.service
%endif

%changelog
* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.111-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Dec 10 2015 Peter Jones <pjones@redhat.com> - 0.111-7
- Obsolete pesign-rh-test-certs, it was in -1's update.
  Resolves: rhbz#1283475

* Wed Dec 02 2015 Peter Jones <pjones@redhat.com> - 0.111-6
- *Don't* use --certdir if we're using the socket.
  Related: rhbz#1283475
  Related: rhbz#1284063
  Related: rhbz#1284561

* Tue Dec 01 2015 Peter Jones <pjones@redhat.com> - 0.111-5
- Actually do a better job of choosing which cert to use when, so people will
  stop seeing any of this problem.  (Thanks for the thought, jforbes.)
  Resolves: rhbz#1283475
  Resolves: rhbz#1284063
  Resolves: rhbz#1284561

* Mon Nov 30 2015 Peter Jones <pjones@redhat.com> - 0.111-5
- setfacl even harder.
  Related: rhbz#1283475
  Related: rhbz#1284063
  Related: rhbz#1284561

* Fri Nov 20 2015 Peter Jones <pjones@redhat.com> - 0.111-3
- Better ACL setting code.
  Related: rhbz#1283475

* Thu Nov 19 2015 Peter Jones <pjones@redhat.com> - 0.111-2
- Allow the mockbuild user to read the nss database if the account exists.

* Wed Oct 28 2015 Peter Jones <pjones@redhat.com> - 0.111-1
- Rebase to 0.111
- Split test certs out into a "Recommends" subpackage.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.110-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Mar  4 2015 Ville Skyttä <ville.skytta@iki.fi> - 0.110-2
- Install macros in %%{_rpmconfigdir}/macros.d where available (#1074281)

* Fri Oct 24 2014 Peter Jones <pjones@redhat.com> - 0.110-1
- Update to pesign-0.110

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.108-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.108-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Peter Jones <pjones@redhat.com> - 0.108-2
- Fix a networking problem nirik observed when reinstalling builders.

* Sat Aug 10 2013 Peter Jones <pjones@redhat.com> - 0.108-1
- Remove errant result files and raise an error from %%pesign 

* Tue Aug 06 2013 Peter Jones <pjones@redhat.com> - 0.106-3
- Add code for signing in RHEL 7

* Mon Aug 05 2013 Peter Jones <pjones@redhat.com> - 0.106-2
- Fix for new %%doc rules.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.106-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue May 21 2013 Peter Jones <pjones@redhat.com> - 0.106-1
- Update to 0.106
- Hopefully fix the segfault dgilmore was seeing.

* Mon May 20 2013 Peter Jones <pjones@redhat.com> - 0.105-1
- Various bug fixes.

* Wed May 15 2013 Peter Jones <pjones@redhat.com> - 0.104-1
- Make sure alignment is correct on signature list entries
  Resolves: rhbz#963361
- Make sure section alignment is correct if we have to extend the file

* Wed Feb 06 2013 Peter Jones <pjones@redhat.com> - 0.103-2
- Conditionalize systemd bits so they don't show up in RHEL 6 builds

* Tue Feb 05 2013 Peter Jones <pjones@redhat.com> - 0.103-1
- One more compiler problem.  Let's expect a few more, shall we?

* Tue Feb 05 2013 Peter Jones <pjones@redhat.com> - 0.102-1
- Don't use --std=gnu11 because we have to work on RHEL 6 builders.

* Mon Feb 04 2013 Peter Jones <pjones@redhat.com> - 0.101-1
- Update to 0.101 to fix more "pesign -E" issues.

* Fri Nov 30 2012 Peter Jones <pjones@redhat.com> - 0.100-1
- Fix insertion of signatures from a file.

* Mon Nov 26 2012 Matthew Garrett <mjg59@srcf.ucam.org> - 0.99-9
- Add a patch needed for new shim builds

* Fri Oct 19 2012 Peter Jones <pjones@redhat.com> - 0.99-8
- Get the Fedora signing token name right.

* Fri Oct 19 2012 Peter Jones <pjones@redhat.com>
- Add coolkey and opensc modules to pki database during %%install.

* Fri Oct 19 2012 Peter Jones <pjones@redhat.com> - 0.99-7
- setfacl u:kojibuilder:rw /var/run/pesign/socket
- Fix command line checking in client
- Add client stdin pin reading.

* Thu Oct 18 2012 Peter Jones <pjones@redhat.com> - 0.99-6
- Automatically select daemon as signer when using rpm macros.

* Thu Oct 18 2012 Peter Jones <pjones@redhat.com> - 0.99-5
- Make it work on the -el6 branch as well.

* Wed Oct 17 2012 Peter Jones <pjones@redhat.com> - 0.99-4
- Fix some more bugs found by valgrind and coverity.
- Don't build utils/ ; we're not using them and they're not ready anyway. 

* Wed Oct 17 2012 Peter Jones <pjones@redhat.com> - 0.99-3
- Fix daemon startup bug from 0.99-2

* Wed Oct 17 2012 Peter Jones <pjones@redhat.com> - 0.99-2
- Fix various bugs from 0.99-1
- Don't make the database unreadable just yet.

* Mon Oct 15 2012 Peter Jones <pjones@redhat.com> - 0.99-1
- Update to 0.99
- Add documentation for client/server mode.
- Add --pinfd and --pinfile to server mode.

* Fri Oct 12 2012 Peter Jones <pjones@redhat.com> - 0.98-1
- Update to 0.98
- Add client/server mode.

* Mon Oct 01 2012 Peter Jones <pjones@redhat.com> - 0.10-5
- Fix missing section address fixup.

* Wed Aug 15 2012 Peter Jones <pjones@redhat.com> - 0.10-4
- Make macros.pesign even better (and make it work right for i686 packages)

* Tue Aug 14 2012 Peter Jones <pjones@redhat.com> - 0.10-3
- Only sign things on x86_64; all else ignore gracefully.

* Tue Aug 14 2012 Peter Jones <pjones@redhat.com> - 0.10-2
- Make macros.pesign more reliable

* Mon Aug 13 2012 Peter Jones <pjones@redhat.com> - 0.10-1
- Update to 0.10
- Include rpm macros to support easy custom signing of signed packages.

* Fri Aug 10 2012 Peter Jones <pjones@redhat.com> - 0.9-1
- Update to 0.9
- Bug fix from Gary Ching-Pang Lin
- Support NSS Token selection for use with smart cards.

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com> - 0.8-1
- Update to 0.8
- Don't open the db read-write
- Fix permissions on keystore (everybody can sign with test keys)

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com> - 0.7-2
- Include test keys.

* Mon Jul 30 2012 Peter Jones <pjones@redhat.com> - 0.7-1
- Update to 0.7
- Better fix for MS compatibility.

* Mon Jul 30 2012 Peter Jones <pjones@redhat.com> - 0.6-1
- Update to 0.6
- Bug-for-bug compatibility with signtool.exe .

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Peter Jones <pjones@redhat.com> - 0.5-1
- Rebase to 0.5
- Do more rigorous bounds checking when hashing a new binary.

* Tue Jul 10 2012 Peter Jones <pjones@redhat.com> - 0.3-2
- Rebase to 0.4

* Fri Jun 22 2012 Peter Jones <pjones@redhat.com> - 0.3-2
- Move man page to a more reasonable place.

* Fri Jun 22 2012 Peter Jones <pjones@redhat.com> - 0.3-1
- Update to upstream's 0.3 .

* Thu Jun 21 2012 Peter Jones <pjones@redhat.com> - 0.2-4
- Do not build with smp flags.

* Thu Jun 21 2012 Peter Jones <pjones@redhat.com> - 0.2-3
- Make it build on i686, though it's unclear it'll ever be necessary.

* Thu Jun 21 2012 Peter Jones <pjones@redhat.com> - 0.2-2
- Fix compile problem with f18's compiler.

* Thu Jun 21 2012 Peter Jones <pjones@redhat.com> - 0.2-1
- Fix some rpmlint complaints nirik pointed out
- Add popt-devel build dep

* Fri Jun 15 2012 Peter Jones <pjones@redhat.com> - 0.1-1
- First version of SRPM.
