class_name ClassChangePanel
extends Control
## Change class, free, any time out of battle (Hayden 2026-11-05): every class at
## the tier this character has earned, with no trial or stat check. The player says
## what happens to their spent points: keep, refund, or refund and auto-spend.

signal changed(member: CharacterData, def: ClassDef)
signal closed

var character: CharacterData
var selected: ClassDef
var _group := ButtonGroup.new()

var _title: Label
var _list: VBoxContainer
var _detail: Label
var _mode_buttons: Array[Button] = []


func _init() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false

	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.65)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var panel := PanelContainer.new()
	UIStyle.apply(panel)
	UIStyle.fit_to_screen(panel, Vector2(640, 560))
	center.add_child(panel)

	var margin := MarginContainer.new()
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 16)
	panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	margin.add_child(box)

	_title = Label.new()
	_title.add_theme_font_size_override("font_size", 24)
	box.add_child(_title)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	box.add_child(scroll)
	_list = VBoxContainer.new()
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_list)

	_detail = Label.new()
	_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_detail.custom_minimum_size.y = 64
	box.add_child(_detail)

	var buttons := HFlowContainer.new()
	buttons.alignment = FlowContainer.ALIGNMENT_END
	box.add_child(buttons)
	var modes := [
		["Keep stats", GameState.ClassChangeStats.KEEP, "Change class. Spent points stay where they are."],
		["Refund points", GameState.ClassChangeStats.REFUND, "Change class and refund every spent point to spend yourself."],
		["Refund + auto-spend", GameState.ClassChangeStats.AUTO_SPEND, "Change class, refund every spent point and spend them toward the new class."],
	]
	for m in modes:
		var b := Button.new()
		b.text = m[0]
		b.tooltip_text = m[2]
		b.disabled = true
		b.pressed.connect(confirm.bind(m[1]))
		buttons.add_child(b)
		_mode_buttons.append(b)
	var cancel := Button.new()
	cancel.text = "Cancel"
	cancel.pressed.connect(close)
	buttons.add_child(cancel)


func open(member: CharacterData) -> void:
	character = member
	selected = null
	var current := member.get_class_def()
	_title.text = "%s: change class" % member.character_name
	_detail.text = "You're a %s. Pick any class at your tier. It's free, and you can change again later." % current.display_name
	for c in _list.get_children():
		c.queue_free()
	_group = ButtonGroup.new()
	for def in GameState.class_change_options(member):
		var b := Button.new()
		b.toggle_mode = true
		b.button_group = _group
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.text = "%s   ·   %s row" % [def.display_name, SkillLibrary.recommended_row_name(def.id)]
		b.pressed.connect(select.bind(def))
		_list.add_child(b)
	for b in _mode_buttons:
		b.disabled = true
	show()


func select(def: ClassDef) -> void:
	selected = def
	_detail.text = "%s\nUses %s (you have %d%% there)." % [def.description, def.requirement_text(),
		roundi(def.qualification_share(character.stats) * 100)]
	for b in _mode_buttons:
		b.disabled = false


func confirm(points: int) -> void:
	var def := selected
	if def and GameState.change_class(character, def, points):
		CutIns.play(CutInData.class_change(character, def, true))
		changed.emit(character, def)
		close()


func close() -> void:
	hide()
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()
