# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#


class KiwiError(Exception):
    """
        Base class to handle all known exceptions. Specific exceptions
        are sub classes of this base class
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return format(self.message)


class KiwiBootStrapPhaseFailed(KiwiError):
    pass


class KiwiCommandError(KiwiError):
    pass


class KiwiCommandNotLoaded(KiwiError):
    pass


class KiwiCompressionFormatUnknown(KiwiError):
    pass


class KiwiConfigFileNotFound(KiwiError):
    pass


class KiwiDataStructureError(KiwiError):
    pass


class KiwiDescriptionInvalid(KiwiError):
    pass


class KiwiFileNotFound(KiwiError):
    pass


class KiwiHelpNoCommandGiven(KiwiError):
    pass


class KiwiInstallPhaseFailed(KiwiError):
    pass


class KiwiInvalidVolumeName(KiwiError):
    pass


class KiwiLoadCommandUndefined(KiwiError):
    pass


class KiwiLogFileSetupFailed(KiwiError):
    pass


class KiwiLoopSetupError(KiwiError):
    pass


class KiwiMountKernelFileSystemsError(KiwiError):
    pass


class KiwiMountSharedDirectoryError(KiwiError):
    pass


class KiwiProfileNotFound(KiwiError):
    pass


class KiwiRepoTypeUnknown(KiwiError):
    pass


class KiwiRequestedTypeError(KiwiError):
    pass


class KiwiRootDirExists(KiwiError):
    pass


class KiwiRootInitCreationError(KiwiError):
    pass


class KiwiRpmDatabaseReloadError(KiwiError):
    pass


class KiwiSchemaImportError(KiwiError):
    pass


class KiwiScriptFailed(KiwiError):
    pass


class KiwiSetupIntermediateConfigError(KiwiError):
    pass


class KiwiSystemDeletePackagesFailed(KiwiError):
    pass


class KiwiSystemInstallPackagesFailed(KiwiError):
    pass


class KiwiSystemUpdateFailed(KiwiError):
    pass


class KiwiTargetDirectoryNotFound(KiwiError):
    pass


class KiwiTypeNotFound(KiwiError):
    pass


class KiwiUnknownCommand(KiwiError):
    pass


class KiwiUnknownServiceName(KiwiError):
    pass


class KiwiUriStyleUnknown(KiwiError):
    pass


class KiwiUriTypeUnknown(KiwiError):
    pass


class KiwiValidationError(KiwiError):
    pass
