extends Node2D


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	$Sprite2D.texture.noise.offset.z += 10 * delta
	$Sprite2D2.texture.noise.offset.z += 30 * delta
	pass
