class_name StatAllocationPanel
extends PanelContainer
## Stat allocation UI. Points go into a PENDING pool first and only commit on
## Confirm, so auto-spend and misclicks can be looked over first.
## Built entirely in code so it can be dropped into any scene.

signal allocation_confirmed

var character: CharacterData
var _pending: Dictionary = {}   # Stats.Type -> int
var _rows: Dictionary = {}      # Stats.Type -> { value: Label, minus: Button, plus: Button }
var _points_label: Label
var _hint: Label
var _derived_label: Label
var _confirm_btn: Button
var _clear_btn: Button
var _goal_label: Label
var _auto_btn: Button
var _goal_btn: Button
var _reset_btn: Button
## The open "what are you building toward?" window (tests look at it).
var goal_dialog: AcceptDialog


func _init() -> void:
	custom_minimum_size = Vector2(680, 0)   # wide, so it stays short at 120% interface size
	var margin := MarginContainer.new()
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 16)
	add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	margin.add_child(box)

	var title := Label.new()
	title.text = "Stats"
	title.add_theme_font_size_override("font_size", 24)
	box.add_child(title)

	# What this character's class wants (Hayden 2026-11-04).
	_hint = Label.new()
	_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_hint.add_theme_font_size_override("font_size", 13)
	_hint.modulate = Color(0.85, 0.9, 1.0)
	box.add_child(_hint)
	_points_label = Label.new()
	box.add_child(_points_label)

	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 12)
	var body := HBoxContainer.new()
	body.add_theme_constant_override("separation", 24)
	box.add_child(body)
	body.add_child(grid)
	_derived_label = Label.new()
	body.add_child(_derived_label)

	for stat in Stats.all():
		var name_label := Label.new()
		name_label.text = Stats.name_of(stat)
		name_label.tooltip_text = Stats.description_of(stat)
		name_label.mouse_filter = Control.MOUSE_FILTER_PASS
		name_label.custom_minimum_size.x = 120
		grid.add_child(name_label)

		var value_label := Label.new()
		value_label.custom_minimum_size.x = 110
		grid.add_child(value_label)

		var minus := Button.new()
		minus.text = " - "
		minus.pressed.connect(_change_pending.bind(stat, -1))
		grid.add_child(minus)

		var plus := Button.new()
		plus.text = " + "
		plus.pressed.connect(_change_pending.bind(stat, 1))
		grid.add_child(plus)

		_rows[stat] = { "value": value_label, "minus": minus, "plus": plus }

	var buttons := HBoxContainer.new()
	box.add_child(buttons)
	_confirm_btn = Button.new()
	_confirm_btn.text = "Confirm"
	_confirm_btn.pressed.connect(_on_confirm)
	buttons.add_child(_confirm_btn)
	_clear_btn = Button.new()
	_clear_btn.text = "Clear pending"
	_clear_btn.pressed.connect(_clear_pending)
	buttons.add_child(_clear_btn)

	_goal_label = Label.new()
	_goal_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_goal_label.add_theme_font_size_override("font_size", 13)
	box.add_child(_goal_label)
	var auto_row := HFlowContainer.new()
	box.add_child(auto_row)
	_auto_btn = Button.new()
	_auto_btn.text = "Auto-spend"
	_auto_btn.tooltip_text = "Fills in your points toward the class you're building for. Nothing is spent until you Confirm."
	_auto_btn.pressed.connect(auto_spend)
	auto_row.add_child(_auto_btn)
	_goal_btn = Button.new()
	_goal_btn.text = "Change goal"
	_goal_btn.pressed.connect(_ask_goal.bind(false))
	auto_row.add_child(_goal_btn)
	_reset_btn = Button.new()
	_reset_btn.text = "Reset stats (free)"
	_reset_btn.tooltip_text = "Refunds every spent point. Your class stays."
	_reset_btn.pressed.connect(_confirm_reset)
	auto_row.add_child(_reset_btn)


	_clear_pending_silent()


func bind(c: CharacterData) -> void:
	if character and character.stats_changed.is_connected(_refresh):
		character.stats_changed.disconnect(_refresh)
	character = c
	character.stats_changed.connect(_refresh)
	_clear_pending()


func pending_total() -> int:
	var sum := 0
	for stat in _pending:
		sum += _pending[stat]
	return sum


func _remaining() -> int:
	return character.unspent_points - pending_total() if character else 0


func _change_pending(stat: int, delta: int) -> void:
	if character == null:
		return
	if delta > 0 and _remaining() <= 0:
		return
	_pending[stat] = maxi(0, _pending[stat] + delta)
	_refresh()


func _clear_pending_silent() -> void:
	for stat in Stats.all():
		_pending[stat] = 0


func _clear_pending() -> void:
	_clear_pending_silent()
	_refresh()


func _on_confirm() -> void:
	if character and character.apply_allocation(_pending.duplicate()):
		_clear_pending()
		allocation_confirmed.emit()


## Fills the pending pool toward the goal, asking for the goal first if there's a choice.
func auto_spend() -> void:
	if character == null or _remaining() <= 0:
		return
	if character.needs_goal_choice():
		_ask_goal(true)
	else:
		_fill_auto()


func _fill_auto() -> void:
	var plan := character.auto_spend_plan(character.goal_class(), _remaining(), _pending)
	for stat in plan:
		_pending[stat] += plan[stat]
	_refresh()


## Sets the goal (the pop-up's buttons call this).
func pick_goal(def: ClassDef, then_spend: bool) -> void:
	character.build_goal = def.id
	if goal_dialog:
		goal_dialog.queue_free()
		goal_dialog = null
	if then_spend:
		_fill_auto()
	else:
		_refresh()


func _ask_goal(then_spend: bool) -> void:
	if goal_dialog:
		goal_dialog.queue_free()
	goal_dialog = AcceptDialog.new()
	goal_dialog.title = "Build toward"
	goal_dialog.ok_button_text = "Cancel"
	var box := VBoxContainer.new()
	var ask := Label.new()
	ask.text = "What is %s trying to become?" % character.character_name
	box.add_child(ask)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(520, 320)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	box.add_child(scroll)
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)
	for def in character.goal_options():
		var b := Button.new()
		b.text = "%s: %s (now %d%%)" % [def.display_name, def.requirement_text(), roundi(def.qualification_share(character.stats) * 100)]
		b.tooltip_text = def.description
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.pressed.connect(pick_goal.bind(def, then_spend))
		list.add_child(b)
	goal_dialog.add_child(box)
	goal_dialog.canceled.connect(_close_goal)
	goal_dialog.confirmed.connect(_close_goal)
	add_child(goal_dialog)
	goal_dialog.popup_centered()


func _close_goal() -> void:
	if goal_dialog:
		goal_dialog.queue_free()
		goal_dialog = null


func _confirm_reset() -> void:
	var dlg := ConfirmationDialog.new()
	dlg.title = "Reset stats"
	dlg.dialog_text = "Refund all of %s's spent stat points? It's free, and the class stays." % character.character_name
	dlg.confirmed.connect(func():
		character.respec()
		_clear_pending()
		dlg.queue_free())
	dlg.canceled.connect(dlg.queue_free)
	add_child(dlg)
	dlg.popup_centered()


func _refresh() -> void:
	if character == null:
		return
	# Clamp pending if points vanished (e.g. external change).
	if _remaining() < 0:
		_clear_pending_silent()

	_hint.text = character.build_hint()
	var remaining := _remaining()
	_points_label.text = "Unspent points: %d" % remaining
	if pending_total() > 0:
		_points_label.text += "   (%d pending)" % pending_total()

	for stat in Stats.all():
		var row: Dictionary = _rows[stat]
		var total := character.stats.get_total(stat)
		var pend: int = _pending[stat]
		row.value.text = "%d" % total if pend == 0 else "%d  → %d" % [total, total + pend]
		row.value.modulate = Color(0.55, 1.0, 0.55) if pend > 0 else Color.WHITE
		row.minus.disabled = pend <= 0
		row.plus.disabled = remaining <= 0

	var goal := character.goal_class()
	var options := character.goal_options()
	if goal == null:
		_goal_label.text = "Auto-spend will ask what you're building toward."
	elif options.is_empty():
		_goal_label.text = "Auto-spend: building on your class's own stats."
	else:
		_goal_label.text = "Building toward: %s (needs %s, now %d%%)." % [goal.display_name, goal.requirement_text(),
			roundi(goal.qualification_share(character.stats) * 100)]
	_auto_btn.disabled = remaining <= 0
	_goal_btn.visible = options.size() > 1
	_reset_btn.disabled = not character.can_respec()
	_confirm_btn.disabled = pending_total() == 0
	_clear_btn.disabled = pending_total() == 0

	var s := character.stats
	_derived_label.text = "Max HP: %d\nPhys DEF: %.1f   Mag DEF: %.1f\nDodge: %.1f%%   Crit: %.1f%%\nTurn priority: %d" % [
		s.max_hp(), s.physical_defense(), s.magic_defense(),
		s.dodge_chance() * 100.0, s.crit_chance() * 100.0, s.turn_priority()]
