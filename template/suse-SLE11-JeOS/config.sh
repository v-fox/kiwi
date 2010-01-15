#!/bin/bash
#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig
test -f /.profile && . /.profile

#======================================
# Greeting...
#--------------------------------------
echo "Configure image: [$kiwi_iname]..."

#======================================
# Activate services
#--------------------------------------
suseActivateDefaultServices
suseRemoveService sshd
suseRemoveService gpm
suseRemoveService nfs

#======================================
# Setup baseproduct link
#--------------------------------------
suseSetupProduct

#======================================
# Add missing gpg keys to rpm
#--------------------------------------
suseImportBuildKey

#==========================================
# remove unneeded packages
#------------------------------------------
suseRemovePackagesMarkedForDeletion
        
#======================================
# Remove all documentation
#--------------------------------------
baseStripDocs

#======================================
# SuSEconfig
#--------------------------------------
suseConfig

#======================================
# Umount kernel filesystems
#--------------------------------------
baseCleanMount

exit 0
