%global libsolv_version 0.7.4-1
%global libmodulemd_version 1.6.1
%global librepo_version 1.9.5
%global dnf_conflict 4.2.5
%global swig_version 3.0.12

%bcond_with valgrind

# Do not build bindings for python3 for RHEL <= 7
%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with python3
%else
%bcond_without python3
%endif

%if 0%{?rhel} > 7 || 0%{?fedora} > 29
# Disable python2 build by default
%bcond_with python2
%else
%bcond_without python2
%endif

%if 0%{?rhel} && ! 0%{?centos}
%bcond_without rhsm
%else
%bcond_with rhsm
%endif

%global _cmake_opts \\\
    -DENABLE_RHSM_SUPPORT=%{?with_rhsm:ON}%{!?with_rhsm:OFF} \\\
    %{nil}

Name:           libdnf
Version:        0.31.0
Release:        4%{?dist}
Summary:        Library providing simplified C and Python API to libsolv
License:        LGPLv2+
URL:            https://github.com/rpm-software-management/libdnf
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Patch0001:      0001-Revert-9309e92332241ff1113433057c969cebf127734e.patch
Patch0002:      0002-Reintroduce-hawkeyRepo-deprecated-for-compatibility.patch
Patch0003:      0003-hawkeyRepo-add-deprecation-message.patch
Patch0004:      0004-Unit-tests-for-reintroduced-hawkeyRepo.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1355764#c50
Patch0005:      0005-Set-relevant-g_log-domain-handlers-instead-of-a-default-one.patch
Patch0006:      0006-Add-a-debug-argument-to-LibrepologaddHandler.patch
Patch0007:      0007-Add-a-logdebug-argument-to-hawkeySack.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libsolv-devel >= %{libsolv_version}
BuildRequires:  pkgconfig(librepo) >= %{librepo_version}
BuildRequires:  pkgconfig(check)
%if %{with valgrind}
BuildRequires:  valgrind
%endif
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.46.0
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  rpm-devel >= 4.11.0
%if %{with rhsm}
BuildRequires:  pkgconfig(librhsm) >= 0.0.3
%endif
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(json-c)
BuildRequires:  pkgconfig(cppunit)
BuildRequires:  pkgconfig(libcrypto)
BuildRequires:  pkgconfig(modulemd) >= %{libmodulemd_version}
BuildRequires:  pkgconfig(smartcols)
BuildRequires:  gettext
BuildRequires:  gpgme-devel

Requires:       libmodulemd%{?_isa} >= %{libmodulemd_version}
Requires:       libsolv%{?_isa} >= %{libsolv_version}
Requires:       librepo%{?_isa} >= %{librepo_version}

%description
A Library providing simplified C and Python API to libsolv.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsolv-devel%{?_isa} >= %{libsolv_version}

%description devel
Development files for %{name}.

%if %{with python2}
%package -n python2-%{name}
%{?python_provide:%python_provide python2-%{name}}
Summary:        Python 2 bindings for the libdnf library.
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python2-devel
%if 0%{?rhel} == 7
BuildRequires:  python-sphinx
BuildRequires:  swig3 >= %{swig_version}
%else
BuildRequires:  python2-sphinx
BuildRequires:  swig >= %{swig_version}
%endif

%description -n python2-%{name}
Python 2 bindings for the libdnf library.
%endif # with python2

%if %{with python3}
%package -n python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:        Python 3 bindings for the libdnf library.
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python3-devel
BuildRequires:  python3-sphinx
BuildRequires:  swig >= %{swig_version}

%description -n python3-%{name}
Python 3 bindings for the libdnf library.
%endif

%if %{with python2}
%package -n python2-hawkey
Summary:        Python 2 bindings for the hawkey library
%{?python_provide:%python_provide python2-hawkey}
BuildRequires:  python2-devel
%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires:  python-nose
%else
BuildRequires:  python2-nose
%endif
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python2-%{name} = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python2-dnf >= 2.0.0
Conflicts:      python2-dnf < %{dnf_conflict}
Conflicts:      python-dnf < %{dnf_conflict}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.
%endif # with python2

%if %{with python3}
%package -n python3-hawkey
Summary:        Python 3 bindings for the hawkey library
%{?python_provide:%python_provide python3-hawkey}
BuildRequires:  python3-devel
BuildRequires:  python3-nose
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-%{name} = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python3-dnf >= 2.0.0
Conflicts:      python3-dnf < %{dnf_conflict}
# Obsoletes F27 packages
Obsoletes:      platform-python-hawkey < %{version}-%{release}

%description -n python3-hawkey
Python 3 bindings for the hawkey library.
%endif

%prep
%autosetup -p1
%if %{with python2}
mkdir build-py2
%endif # with python2
%if %{with python3}
mkdir build-py3
%endif

%build
%if %{with python2}
pushd build-py2
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python2} -DWITH_MAN=OFF ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd
%endif # with python2

%if %{with python3}
pushd build-py3
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python3} -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd
%endif

%check
if [ "$(id -u)" == "0" ] ; then
        cat <<ERROR 1>&2
Package tests cannot be run under superuser account.
Please build the package as non-root user.
ERROR
        exit 1
fi

%if %{with python2}
pushd build-py2
  make ARGS="-V" test
popd
%endif # with python2
%if %{with python3}
# Run just the Python tests, not all of them, since
# we have coverage of the core from the first build
pushd build-py3/python/hawkey/tests
  make ARGS="-V" test
popd
%endif

%install
%if %{with python2}
pushd build-py2
  %make_install
popd
%endif # with python2
%if %{with python3}
pushd build-py3
  %make_install
popd
%endif

%find_lang %{name}

%if 0%{?rhel} && 0%{?rhel} <= 7
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%else
%ldconfig_scriptlets
%endif

%files -f %{name}.lang
%license COPYING
%doc README.md AUTHORS
%{_libdir}/%{name}.so.*
%{_libdir}/libdnf/plugins/README

%files devel
%doc %{_datadir}/gtk-doc/html/%{name}/
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/

%if %{with python2}
%files -n python2-%{name}
%{python2_sitearch}/%{name}/
%endif # with python2

%if %{with python3}
%files -n python3-%{name}
%{python3_sitearch}/%{name}/
%endif

%if %{with python2}
%files -n python2-hawkey
%{python2_sitearch}/hawkey/
%endif # with python2

%if %{with python3}
%files -n python3-hawkey
%{python3_sitearch}/hawkey/
%endif

%changelog
* Wed Jul 24 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.31.0-4
- Backport patches to not log DEBUG messages by default (RhBug:1355764)

* Fri May 03 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.31.0-3
- Backport patches to reintroduce hawkeyRepo

* Thu Apr 25 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.31.0-1
- Update to 0.31.0
- Installroot now requires absolute path
- Support "_none_" value for repo option "proxy" (RhBug:1680272)
- Add support for Module advisories
- Add support for xml:base attribute from primary.xml (RhBug:1691315)
- Improve detection of Platform ID (RhBug:1688462)

* Wed Mar 27 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.28.1-1
- Update to 0.28.1
- Return empty query if incorrect reldep (RhBug:1687135)
- ConfigParser: Improve compatibility with Python ConfigParser and dnf-plugin-spacewalk (RhBug:1692044)
- ConfigParser: Unify default set of string represenation of boolean values
- Fix segfault when interrupting dnf process (RhBug:1610456)

* Mon Mar 11 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.28.0-1
- Update to 0.28.0
- Exclude module pkgs that have conflict
- Enhance config parser to preserve order of data, and keep comments and format
- Improve ARM detection
- Add support for SHA-384

* Wed Feb 13 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.26.0-1
- Update to 0.26.0-1
- Enhance modular solver to handle enabled and default module streams differently (RhBug:1648839)
- Add support of wild cards for modules (RhBug:1644588)
- Revert commit that adds best as default behavior

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.24.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Dec 12 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.24.1-1
- Update to 0.24.1
- Add support for zchunk
- Enhance LIBDNF plugins support
- Enhance sorting for module list (RhBug:1590358)
- [repo] Check whether metadata cache is expired (RhBug:1539620,1648274)
- [DnfRepo] Add methods for alternative repository metadata type and download (RhBug:1656314)
- Remove installed profile on module  enable or disable (RhBug:1653623)
- [sack] Implement dnf_sack_get_rpmdb_version()

* Thu Nov 22 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.3-1
- Permanently disable Python2 build for Fedora 30+
- Update to 0.22.3
- Modify solver_describe_decision to report cleaned (RhBug:1486749)
- [swdb] create persistent WAL files (RhBug:1640235)
- Relocate ModuleContainer save hook (RhBug:1632518)
- [transaction] Fix transaction item lookup for obsoleted packages (RhBug: 1642796)
- Fix memory leaks and memory allocations
- [repo] Possibility to extend downloaded repository metadata

* Wed Nov 07 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-8
- Backport fixes for RHBZ#1642796 from upstream master

* Tue Oct 30 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.22.0-7
- Rebuild for libsolv 0.7

* Tue Oct 23 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-6
- Add patch Relocate-ModuleContainer-save-hook-RhBug1632518
- Add patch Test-if-sack-is-present-and-run-save-module-persistor-RhBug1632518

* Sat Oct 20 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-5
- remove problematic patch Relocate-ModuleContainer-save-hook-RhBug1632518

* Fri Oct 19 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-4
- backport Relocate-ModuleContainer-save-hook-RhBug1632518

* Thu Oct 18 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-3
- bacport swdb-create-persistent-WAL-files-RhBug1640235

* Wed Oct 17 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-2
- backport Modify-solver_describe_decision-to-report-cleaned-RhBug1486749
- backport history-Fix-crash-in-TransactionItemaddReplacedBy

* Mon Oct 15 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.22.0-1
- Update to 0.22.0
- Fix segfault in repo_internalize_trigger (RhBug:1375895)
- Change sorting of installonly packages (RhBug:1627685)
- [swdb] Fixed pattern searching in history db (RhBug:1635542)
- Check correctly gpg for repomd when refresh is used (RhBug:1636743)
- [conf] Provide additional VectorString methods for compatibility with Python list.
- [plugins] add plugin loading and hooks into libdnf

* Sat Sep 29 2018 Kevin Fenzi <kevin@scrye.com> - 0.20.0-2
- Temp re-enable python2 subpackages to get rawhide composing again.

* Tue Sep 25 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.20.0-1
- [module] Report module solver errors
- [module] Enhance module commands and errors
- [transaction] Fixed several problems with SWDB
- Remove unneeded regex URL tests (RhBug:1598336)
- Allow quoted values in ini files (RhBug:1624056)
- Filter out not unique set of solver problems (RhBug:1564369)
- Disable python2 build for Fedora 30+

* Tue Sep 18 2018 Adam Williamson <awilliam@redhat.com> - 0.19.1-3
- Backport PR #585 for an update crash bug (#1629340)

* Fri Sep 14 2018 Kalev Lember <klember@redhat.com> - 0.19.1-2
- Backport a fix for a packagekit crasher / F29 Beta blocker (#1626851)

* Mon Sep 10 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.19.1-1
- Fix compilation errors on gcc-4.8.5
- [module] Allow module queries on disabled modules

* Fri Sep 07 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.19.0-1
- [query] Reldeps can contain a space char (RhBug:1612462)
- [transaction] Avoid adding duplicates via Transaction::addItem()
- Fix compilation errors on gcc-4.8.5
- [module] Make available ModuleProfile using SWIG
- [module] Redesign module disable and reset

* Mon Aug 13 2018 Daniel Mach <dmach@redhat.com> - 0.17.2-1
- [sqlite3] Change db locking mode to DEFAULT.
- [doc] Add libsmartcols-devel to devel deps.

* Mon Aug 13 2018 Daniel Mach <dmach@redhat.com> - 0.17.1-1
- [module] Solve a problem in python constructor of NSVCAP if no version.
- [translations] Update translations from zanata.
- [transaction] Fix crash after using dnf.comps.CompsQuery and forking the process in Anaconda.
- [module] Support for resetting module state.
- [output] Introduce wrapper for smartcols.

* Fri Aug 10 2018 Adam Williamson <awilliam@redhat.com> - 0.17.0-2
- Backport fix that prevented anaconda running dnf in a subprocess (#546)

* Tue Aug 07 2018 Daniel Mach <dmach@redhat.com> - 0.17.0-1
- [conf] Add module_platform_id option.
- [module] Add ModulePackageContainer class.
- [module] Add ModulePersistor class.
- [sack] Module filtering made available in python API
- [sack] Module auto-enabling according to installed packages

* Fri Jul 27 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.16.1-3
- Rebuild for new binutils

* Fri Jul 27 2018 Daniel Mach <dmach@redhat.com> - 0.16.1-2
- [module] Implement 'module_hotfixes' conf option to skip filtering RPMs from hotfix repos.
- [goal] Fix distupgrade filter, allow downgrades.
- [context] Allow to set module platform in context.
- [module] Introduce proper modular dependency solving.
- [module] Platform pseudo-module based on /etc/os-release.
- [goal] Add Goal::listSuggested().
- [l10n] Support for translations, add gettext build dependency.

* Sun Jul 22 2018 Daniel Mach <dmach@redhat.com> - 0.16.0-1
- Fix RHSM plugin
- Add support for logging
- Bump minimal libmodulemd version to 1.6.1

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.15.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.15.2-1
- Update to 0.15.1
- Resolves: rhbz#1595487

* Fri Jun 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.15.1-2
- Restore proper ldconfig_scriptlets

* Tue Jun 26 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.15.1-1
- Update to 0.15.1

* Fri Jun 15 2018 Miro Hrončok <mhroncok@redhat.com> - 0.11.1-6
- Rebuilt for Python 3.7

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 30 2018 Igor Gnatenko <ignatenko@redhat.com> - 0.11.1-4
- Switch to %%ldconfig_scriptlets

* Tue Nov 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.11.1-3
- Use better Obsoletes for platform-python

* Fri Nov 03 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.11.1-2
- Remove platform-python subpackage

* Mon Oct 16 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.11.1-1
- Rerelease of 0.11.1-1
- Improvement query performance
- Run file query in hy_subject_get_best_solution only for files (arguments that start with ``/`` or
  ``*/``)
- Resolves: rhbz#1498207 - DNF crash during upgrade installation F26 -> F27

* Tue Oct 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.11.0-1
- Update to 0.11.0

* Mon Oct 02 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.10.1-2
- Rerelease of 0.10.1-1

* Wed Sep 27 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.10.1-1
- Update to 0.10.1
- It improves query performance with name and arch filters. Also nevra filter will now
  handle string with or without epoch.
- Additionally for python bindings it renames NEVRA._has_just_name() to NEVRA.has_just_name() due
  to movement of code into c part of library.
- Resolves: rhbz#1260242 - --exclude does not affect dnf remove's removal of requirements
- Resolves: rhbz#1485881 - DNF claims it cannot install package, which have been already installed
- Resolves: rhbz#1361187 - [abrt] python-ipython-console: filter_updown(): python3.5 killed by SIGABRT

* Fri Sep 15 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-8
- Disable platform python on old releases

* Tue Aug 15 2017 Lumír Balhar <lbalhar@redhat.com> - 0.9.3-7
- Add platform-python subpackage

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-6
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-5
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-4
- Rebuilt for RPM soname bump

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.3-1
- Update to 0.9.3

* Sat Jul 01 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.2-1
- Update to 0.9.2

* Mon Jun 12 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.1-1
- Update to 0.9.1

* Mon May 22 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.0-1
- Update to 0.9.0

* Tue May 02 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.8.2-1
- Update to 0.8.2

* Fri Mar 24 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.8.1-1
- Update to 0.8.1

* Tue Mar 21 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.8.0-1
- Update to 0.8.0

* Mon Feb 20 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.4-1
- Update to 0.7.4

* Fri Feb 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.3-1
- Update to 0.7.3

* Wed Feb 08 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.2-1
- 0.7.2

* Fri Jan 06 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.1-1
- 0.7.1

* Wed Dec 21 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.7.0-0.7gitf9b798c
- Rebuild for Python 3.6

* Mon Dec 19 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.0-0.6gitf9b798c
- Use new upstream URL

* Tue Dec 13 2016 Stratakis Charalampos <cstratak@redhat.com> - 0.7.0-0.5gitf9b798c
- Rebuild for Python 3.6

* Tue Dec 06 2016 Martin Hatina <mhatina@redhat.com> - 0.7.0-0.4gitf9b798c
- Increase conflict version of dnf

* Thu Dec 01 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.0-0.3gitf9b798c
- Update to latest snapshot

* Fri Nov 04 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.2git8bd77f8
- Update to latest snapshot

* Thu Sep 29 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.1git179c0a6
- Initial package
