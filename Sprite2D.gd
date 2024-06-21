extends Sprite2D


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	var img = get_viewport().get_texture().get_image()
	var tex = ImageTexture.create_from_image(img)
	texture = tex
