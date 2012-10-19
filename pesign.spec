Summary: Signing utility for UEFI binaries
Name: pesign
Version: 0.99
Release: 8%{?dist}
Group: Development/System
License: GPLv2
URL: https://github.com/vathpela/pesign
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: git gnu-efi nspr nspr-devel nss nss-devel nss-util popt-devel
BuildRequires: coolkey opensc nss-tools
Requires: nspr nss nss-util popt rpm coolkey opensc
Requires(pre): shadow-utils
ExclusiveArch: i686 x86_64 ia64

# there is no tarball at github, of course.  To get this version do:
# git clone https://github.com/vathpela/pesign.git
# git checkout %%{version}
Source0: pesign-%{version}.tar.bz2
Source1: rh-test-certs.tar.bz2

Patch1: 0001-Use-PK11_TraverseCertsForNicknameInSlot-after-all.patch
Patch2: 0002-Remove-an-unused-field.patch
Patch3: 0003-Free-the-certificate-list-we-make-once-we-re-done-us.patch
Patch4: 0004-Make-sure-we-actually-look-up-the-certificate-when-n.patch
Patch5: 0005-Fix-check-for-allocations-on-tokenname-certname.patch
Patch6: 0006-Update-valgrind.supp-for-newer-codepaths.patch
Patch7: 0007-Free-the-pid-string-once-we-re-done-writing-it.patch
Patch8: 0008-valgrind-Don-t-complain-about-unlocking-a-key-and-ke.patch
Patch9: 0009-Only-try-to-register-OIDs-once.patch
Patch10: 0010-Check-for-NSS_Shutdown-failure.patch
Patch11: 0011-Don-t-destroy-stdin-stdout-stderr-if-we-don-t-fork.patch
Patch12: 0012-valgrind-Add-SECMOD_LoadModule-codepath.patch
Patch13: 0013-Don-t-set-up-digests-in-cms_context_init.patch
Patch14: 0014-Do-register_oids-where-we-re-doing-NSS_Init.patch
Patch15: 0015-Make-daemon-shutdown-actually-close-the-NSS-database.patch
Patch16: 0016-Reformat-a-bunch-of-error-messages-to-be-vaguely-con.patch
Patch17: 0017-Use-PORT_ArenaStrdup-where-appropriate.patch
Patch18: 0018-Minor-whitespace-fixes.patch
Patch19: 0019-daemon-Make-sure-inpe-is-initialized-before-all-erro.patch
Patch20: 0020-Allocate-pesign_context-rather-than-having-it-on-the.patch
Patch21: 0021-pesign-initialize-nss-only-if-we-re-not-a-daemon.patch
Patch22: 0022-Handle-errors-on-pesign_context_init.patch
Patch23: 0023-Add-sanity-checking-to-make-sure-we-don-t-emit-unini.patch
Patch24: 0024-Make-sure-we-free-the-token-cert-we-get-from-the-com.patch
Patch25: 0025-pesign-Only-shut-down-nss-in-pesign.c-if-we-re-not-t.patch
Patch26: 0026-Rework-setup_digests-and-teardown_digests.patch
Patch27: 0027-We-shouldn-t-need-Environment-NSS_STRICT_NOFORK-DISA.patch
Patch28: 0028-Fix-errors-found-by-coverity.patch
Patch29: 0029-Don-t-keep-the-DEPS-list-twice.patch
Patch30: 0030-Don-t-build-util-right-now.patch
Patch31: 0031-Make-install_systemd-and-install_sysvinit-separate-t.patch
Patch32: 0032-Get-rid-of-an-unnecessary-allocation.patch
Patch33: 0033-Allow-use-of-e-from-rpm-macro.patch
Patch34: 0034-Make-client-use-e-like-pesign-does-rather-than-detac.patch
Patch35: 0035-Fix-shutdown-by-systemd-to-remove-socket-and-pidfile.patch
Patch36: 0036-Make-the-macros-use-the-default-fedora-signer-if-the.patch
Patch37: 0037-Fix-command-line-checking-for-s.patch
Patch38: 0038-Add-support-to-read-the-pin-from-stdin-in-client.patch
Patch39: 0039-Fix-token-auth-authentication-failure-error-reportin.patch
Patch40: 0040-Use-setfacl-in-sysvinit-script-to-allow-kojibuilder-.patch
Patch41: 0041-Don-t-return-quite-so-immediately-if-we-re-the-paren.patch
Patch42: 0042-Get-the-Fedora-signing-token-name-right.patch

%description
This package contains the pesign utility for signing UEFI binaries as
well as other associated tools.

%prep
%setup -q -a 1
git init
git config user.email "pesign-owner@fedoraproject.org"
git config user.name "Fedora Ninjas"
git add .
git commit -a -q -m "%{version} baseline."
git am %{patches} </dev/null

%build
make PREFIX=%{_prefix} LIBDIR=%{_libdir}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_libdir}
make PREFIX=%{_prefix} LIBDIR=%{_libdir} INSTALLROOT=%{buildroot} \
	install install_systemd

# there's some stuff that's not really meant to be shipped yet
rm -rf %{buildroot}/boot %{buildroot}/usr/include
rm -rf %{buildroot}%{_libdir}/libdpe*
mv rh-test-certs/etc/pki/pesign/* %{buildroot}/etc/pki/pesign/

modutil -dbdir /etc/pki/pesign -add coolkey \
	-libfile %{_libdir}pkcs11/libcoolkeypk11.so
modutil -dbdir /etc/pki/pesign -add opensc \
	-libfile %{_libdir}/pkcs11/opensc-pkcs11.so

%clean
rm -rf %{buildroot}

%pre
getent group pesign >/dev/null || groupadd -r pesign
getent passwd pesign >/dev/null || \
	useradd -r -g pesign -d /var/run/pesign -s /sbin/nologin \
		-c "Group for the pesign signing daemon" pesign
exit 0

%post
%systemd_post pesign.service

%preun
%systemd_preun pesign.service

%postun
%systemd_postun_with_restart pesign.service

%files
%defattr(-,root,root,-)
%doc README TODO COPYING
%{_bindir}/pesign
%{_bindir}/pesign-client
%{_sysconfdir}/popt.d/pesign.popt
%{_sysconfdir}/rpm/macros.pesign
%{_mandir}/man*/*
%{_unitdir}/pesign.service
%{_prefix}/lib/tmpfiles.d/pesign.conf
%dir %attr(0775,pesign,pesign) /etc/pki/pesign
%attr(0664,pesign,pesign) /etc/pki/pesign/*
%dir %attr(0770, pesign, pesign) %{_localstatedir}/run/%{name}
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/socket
%ghost %attr(0660, -, -) %{_localstatedir}/run/%{name}/pesign.pid

%changelog
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
