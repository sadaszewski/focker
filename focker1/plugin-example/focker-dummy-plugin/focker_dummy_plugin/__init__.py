def on_focker_start():
    print('Woohoo focker starting woohoo!')

def on_focker_pre_command_image_list(args):
    print('!!! About to list images !!!')

def on_focker_create_parser(parser, parser_dict):
    parser_dict['image.build'].add_argument('--foo-bar', type=str)
