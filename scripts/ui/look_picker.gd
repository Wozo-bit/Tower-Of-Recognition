class_name LookPicker
extends HBoxContainer
## "< [portrait] >": picks one of CharacterData.LOOK_COUNT looks for the player
## ("player") or the childhood friend ("childhood_friend"). Shows
## portraits/<who>_<look>.png, or a numbered placeholder until the art exists.
## Used by the test client (New Game) and Tab -> party -> Look.

signal changed(look: int)

const PREVIEW := Vector2(72, 72)

var who := "player"
var look := 0
var _art: TextureRect
var _placeholder: Label
var _caption: Label


func _init(p_who: String = "player", p_look: int = 0) -> void:
	who = p_who
	look = clampi(p_look, 0, CharacterData.LOOK_COUNT - 1)
	alignment = BoxContainer.ALIGNMENT_CENTER
	add_theme_constant_override("separation", 10)
	var prev := Button.new()
	prev.text = "<"
	prev.tooltip_text = "Previous look"
	prev.pressed.connect(step.bind(-1))
	add_child(prev)
	var frame := PanelContainer.new()
	frame.custom_minimum_size = PREVIEW
	add_child(frame)
	_art = TextureRect.new()
	_art.custom_minimum_size = PREVIEW
	_art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	frame.add_child(_art)
	_placeholder = Label.new()
	_placeholder.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_placeholder.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	frame.add_child(_placeholder)
	var next := Button.new()
	next.text = ">"
	next.tooltip_text = "Next look"
	next.pressed.connect(step.bind(1))
	add_child(next)
	_caption = Label.new()
	add_child(_caption)
	_refresh()


## Moves to the next (+1) or previous (-1) look, wrapping round.
func step(by: int) -> void:
	set_look(posmod(look + by, CharacterData.LOOK_COUNT))


func set_look(v: int) -> void:
	look = clampi(v, 0, CharacterData.LOOK_COUNT - 1)
	_refresh()
	changed.emit(look)


func _refresh() -> void:
	var tex := Assets.texture("portraits", Assets.look_id(who, look))
	_art.texture = tex
	_placeholder.visible = tex == null
	_placeholder.text = "Look %d" % (look + 1)
	_caption.text = "%d / %d%s" % [look + 1, CharacterData.LOOK_COUNT, "  (default)" if look == 0 else ""]
