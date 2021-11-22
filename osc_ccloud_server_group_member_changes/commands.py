# Copyright 2021 SAP SE
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from novaclient.v2.server_groups import ServerGroup
from openstackclient.compute.v2.server_group import _formatters, _get_columns
from osc_lib.command import command
from osc_lib import utils


def _add_args(parser):
    parser.add_argument(
        'servergroup',
        metavar='<servergroup_uuid>',
        help='UUID of the server-group'
    )

    parser.add_argument(
        'member',
        metavar='<instance_uuid>',
        nargs='+',
        help=('Instance UUID(s) to add to <servergroup> '
              '(repeat option to add/remove multiple instances)')
    )

    return parser


class BaseMemberCommand(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'servergroup',
            metavar='<servergroup_uuid>',
            help='UUID of the server-group'
        )

        parser.add_argument(
            'member',
            metavar='<instance_uuid>',
            nargs='+',
            help=('Instance UUID(s) to add to <servergroup> '
                  '(repeat option to add/remove multiple instances)')
        )

        return parser

    def take_action(self, parsed_args):
        client_manager = self.app.client_manager
        key = '{}_members'.format(self.operation)
        payload = {key: [str(m) for m in parsed_args.member]}

        url = '/os-server-groups/{}'.format(parsed_args.servergroup)
        headers = {
            'Accept': 'application/json',
            'OpenStack-API-Version': 'compute 2.64'
        }
        resp, body = client_manager.compute.client.put(
            url, json=payload, headers=headers)

        if resp.status_code == 404:
            raise Exception("Error: Could not find server-group {}"
                            .format(parsed_args.servergroup))
        if resp.status_code == 401:
            raise Exception("Error: Insufficient permissions: {}"
                            .format(resp.text))
        if resp.status_code != 200:
            raise Exception("Error: API returned {} - {}"
                            .format(resp.status_code, resp.text))

        # NOTE This is the same code as openstackclient uses to format a
        # server-group.
        content = body['server_group']
        group = ServerGroup(self, content, loaded=True, resp=resp)
        info = {}
        info.update(group._info)

        columns = _get_columns(info)
        data = utils.get_dict_properties(
            info, columns, formatters=_formatters)
        return columns, data


class AddMembers(BaseMemberCommand):
    operation = 'add'


class RemoveMembers(BaseMemberCommand):
    operation = 'remove'
