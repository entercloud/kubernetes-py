#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.md', which is part of this source code package.
#

from kubernetes.K8sObject import K8sObject
from kubernetes.K8sSecret import K8sSecret

VALID_VOLUME_TYPES = [
    'emptyDir',
    'hostPath',
    'gcePersistentDisk',
    'awsElasticBlockStore',
    # 'nfs',                        .3
    # 'iscsi',
    # 'flocker',
    # 'glusterfs',
    # 'rbd',
    # 'cephfs',
    # 'gitRepo',                    .4
    'secret',
    # 'persistentVolumeClaim',      .5
    # 'downwardAPI',
    # 'azureFileVolume',
    # 'vsphereVolume',
]

VALID_EMPTYDIR_MEDIA = [
    '',
    'Memory'
]


class K8sVolume(K8sObject):

    def __init__(self, config=None, name=None, type=None, mount_path=None, read_only=False):
        if name is None:
            raise SyntaxError('K8sVolume: name: [ {0} ] cannot be None.'.format(name))
        if not isinstance(name, str):
            raise SyntaxError('K8sVolume: name: [ {0} ] must be a string.'.format(name.__class__.__name__))

        if type is None:
            type = 'emptyDir'
        if type is not None and type not in VALID_VOLUME_TYPES:
            raise SyntaxError('K8sVolume: volume_type: [ {0} ] is invalid. Must be in: [ {1} ]'.format(type, VALID_VOLUME_TYPES))

        if mount_path is None:
            raise SyntaxError('K8sVolume: mount_path: [ {0} ] cannot be None.'.format(mount_path))
        if not isinstance(mount_path, str):
            raise SyntaxError('K8sVolume: mount_path: [ {0} ] must be a string.'.format(mount_path))
        if not self._is_valid_path(mount_path):
            raise SyntaxError("K8sVolume: mount_path: [ {0} ] is not a valid path.".format(mount_path))

        if not isinstance(read_only, bool):
            raise SyntaxError('K8sVolume: read_only: [ {0} ] must be a boolean.'.format(read_only.__class__.__name__))

        super(K8sVolume, self).__init__(config=config, name=name, obj_type='Volume')

        self.aws_volume_id = None  # used with type 'awsElasticBlockStore'
        self.fs_type = 'ext4'  # used with types 'awsElasticBlockStore' and 'gcePersistentDisk'
        self.gce_pd_name = None  # used with type 'gcePersistentDisk'
        self.host_path = None  # used with type 'hostPath'
        self.medium = ''  # used with type 'emptyDir'
        self.mount_path = mount_path
        self.read_only = read_only
        self.secret_name = None  # used with type 'secret'
        self.type = type

    @staticmethod
    def _is_valid_path(path):
        # Ugh. What a PITA. # TODO: validate path for unix and windows.
        #
        # re_match = re.match(r'^(([a-zA-Z]:)|((\\|/){1,2}\w+)\$?)((\\|/)(\w[\w ]*.*))+\.([a-zA-Z0-9]+)$', path)
        # if re_match is None:
        #     return False
        return True

    # -------------------------------------------------------------------------------------  emptyDir

    def set_medium(self, medium=None):
        if medium is None:
            medium = ''
        if medium is not None and self.type != 'emptyDir':
            raise SyntaxError('K8sVolume: medium: [ {0} ] can only be used with type [ emptyDir ]'. format(medium))
        if medium not in VALID_EMPTYDIR_MEDIA:
            raise SyntaxError('K8sVolume: medium: [ {0} ] is invalid. Must be in: [ {1} ] '.format(medium, VALID_EMPTYDIR_MEDIA))

        self.medium = medium
        return self

    # -------------------------------------------------------------------------------------  hostPath

    def set_host_path(self, path=None):
        if path is None:
            raise SyntaxError("K8sVolume: path: [ {0} ] cannot be None.".format(path))
        if path is not None and self.type != 'hostPath':
            raise SyntaxError('K8sVolume: path: [ {0} ] can only be used with type [ hostPath ]'.format(path))
        if not self._is_valid_path(path):
            raise SyntaxError("K8sVolume: path: [ {0} ] is not a valid path.".format(path))

        self.host_path = path
        return self

    # -------------------------------------------------------------------------------------  secret

    def set_secret_name(self, secret=None):
        if not isinstance(secret, K8sSecret):
            raise SyntaxError('K8sVolume: secret: [ {0} ] must be a K8sSecret.'.format(secret.__class__.__name__))
        if secret is not None and self.type != 'secret':
            raise SyntaxError('K8sVolume: secret: [ {0} ] can only be used with type [ secret ]'.format(secret.name))

        self.secret_name = secret.name
        return self

    # -------------------------------------------------------------------------------------  awsElasticBlockStore

    def set_volume_id(self, volume_id=None):
        if not isinstance(volume_id, str):
            raise SyntaxError('K8sVolume: volume_id: [ {0} ] must be a string.'.format(volume_id.__class__.__name__))
        if volume_id is not None and self.type != 'awsElasticBlockStore':
            raise SyntaxError('K8sVolume: volume_id: [ {0} ] can only be used with type [ awsElasticBlockStore ]'.format(volume_id))

        self.aws_volume_id = volume_id
        return self

    # -------------------------------------------------------------------------------------  gcePersistentDisk

    def set_pd_name(self, pd_name=None):
        if not isinstance(pd_name, str):
            raise SyntaxError('K8sVolume: pd_name: [ {0} ] must be a string.'.format(pd_name.__class__.__name__))
        if pd_name is not None and self.type != 'gcePersistentDisk':
            raise SyntaxError('K8sVolume: pd_name: [ {0} ] can only be used with type [ awsElasticBlockStore ]'.format(pd_name))

        self.gce_pd_name = pd_name
        return self

    # -------------------------------------------------------------------------------------  aws & gce - fs type

    def set_fs_type(self, fs_type=None):
        if not isinstance(fs_type, str):
            raise SyntaxError('K8sVolume: fs_type: [ {0} ] must be a string.'.format(fs_type.__class__.__name__))
        if fs_type is not None and not (self.type == 'awsElasticBlockStore' or self.type == 'gcePersistentDisk'):
            raise SyntaxError(
                'K8sVolume: fs_type: [ {0} ] can only be used with type [ awsElasticBlockStore ]'.format(fs_type))

        self.fs_type = fs_type
        return self
