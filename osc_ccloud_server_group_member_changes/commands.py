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

        content = body['server_group']
        group = ServerGroup(self, content, loaded=True, resp=resp)

        try:
            from openstackclient.compute.v2.server_group import _get_server_group_columns  # noqa:F401

            return self._format_server_group(group, client_manager.compute.client)
        except ImportError:
            return self._format_server_group_legacy(group)

    def _format_server_group_legacy(self, group):
        """Format the server-group like openstackclient

        Compatible with openstackclient < 6.0.0
        """
        from openstackclient.compute.v2.server_group import _formatters, _get_columns

        info = {}
        info.update(group._info)

        columns = _get_columns(info)
        data = utils.get_dict_properties(
            info, columns, formatters=_formatters)
        return columns, data

    def _format_server_group(self, group, compute_client):
        """Format the server-group like openstackclient

        Compatible with openstackclient >= 6.0.0
        """
        from openstackclient.compute.v2.server_group import _formatters, _get_server_group_columns

        info = {}
        info.update(group._info)

        display_columns, columns = _get_server_group_columns(
            info,
            compute_client,
        )
        data = utils.get_item_properties(
            group, columns, formatters=_formatters
        )
        return display_columns, data


class AddMembers(BaseMemberCommand):
    operation = 'add'


class RemoveMembers(BaseMemberCommand):
    operation = 'remove'
