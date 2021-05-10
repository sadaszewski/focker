from anytree import NodeMixin, RenderTree


class Image(NodeMixin):  # Add Node feature
    def __init__(self, name, sha256, tags, size, creation, parent=None):
        self.name = name
        self.sha256 = sha256
        self.tags = tags
        self.size = size
        self.creation = creation
        self.parent = parent

    def render_tree(self):
        return RenderTree(self)