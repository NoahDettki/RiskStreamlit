import streamlit as st
import random

st.set_page_config("Risiko", page_icon=":game_die:")
st.title("Risiko :game_die:")

def reset():
    st.session_state.initialized = False
    st.session_state.attack_units = 4
    st.session_state.defend_units = 1
    st.session_state.log = []

def throw_dice(attackers: int):
    st.session_state.min_move = attackers
    attack_dice = sorted(random.sample(range(1, 7), attackers), reverse=True)
    defend_dice = sorted(random.sample(range(1, 7), 2 if st.session_state.defend_units > 1 else 1), reverse=True)
    compare_limit = min(len(attack_dice), len(defend_dice))
    attacker_lost = 0
    defender_lost = 0
    log_text = "**A["
    # Display defender dice (excess dice are greyed out)
    for i in range(len(attack_dice)):
        if i < compare_limit:
            if attack_dice[i] > defend_dice[i]:
                st.session_state.defend_units -= 1
                defender_lost += 1
            else:
                st.session_state.attack_units -= 1
                attacker_lost += 1
            log_text += f":red[{attack_dice[i]}]"
        else:
            log_text += f":grey[{attack_dice[i]}]"
        if i < len(attack_dice) - 1:
            log_text += ","
    log_text += "] <-> D["
    for i in range(len(defend_dice)):
        if i < compare_limit:
            log_text += f":blue[{defend_dice[i]}]"
        else:
            log_text += f":grey[{defend_dice[i]}]"
        if i < len(defend_dice) - 1:
            log_text += ","
    log_text += "] "
    for i in range(attacker_lost):
        log_text += f":red[-]"
    for i in range(defender_lost):
        log_text += f":blue[-]"
    log_text += "**"
    st.session_state.log.append(log_text)

if "initialized" not in st.session_state:
    st.session_state.initialized = False

# First the user can setup the attackers and defenders total units
with st.expander("Ausgangssituation", expanded=st.session_state.initialized == False):
    with st.form(key="setup", enter_to_submit=False, border=False):
        attack_units = st.number_input(
            "Gesamtzahl Einheiten im Territorium des :red[Angreifers]",
            min_value=2,
            max_value=100,
            value=4,
            step=1
        )
        defend_units = st.number_input(
            "Gesamtzahl Einheiten im Territorium des :blue[Verteidigers]",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )
        submitted = st.form_submit_button("Kampf starten!", type="primary")
        if submitted:
            st.session_state.attack_units = attack_units
            st.session_state.defend_units = defend_units
            st.session_state.min_move = 0
            st.session_state.log = []
            st.session_state.initialized = True
            st.rerun()

# Then the user select the amount of attack units and roll with a simple button click
if st.session_state.initialized:
    st.markdown(f"**Noch :red[{st.session_state.attack_units} Angreifer] vs. :blue[{st.session_state.defend_units} Verteidiger]**")
    if st.session_state.attack_units <= 1:
        st.markdown(f"Der :red[Angreifer] kann mit nur :red[1] Einheit nicht mehr angreifen!")
        st.button("Reset", type="primary", on_click=reset)
    elif st.session_state.defend_units <= 0:
        st.markdown(f"Der :blue[Verteidiger] hat alle Einheiten verloren. Der :red[Angreifer] muss mindestens :red[{st.session_state.min_move}] Einheiten in das eroberte Gebiet setzen!")
        st.button("Reset", type="primary", on_click=reset)
    else:
        max_attack_units = min(3, st.session_state.attack_units-1)
        attack_with = st.slider(
            "Anzahl Einheiten, die der Angreifer einsetzen möchte",
            min_value=1,
            max_value=max(2, max_attack_units),
            value=max_attack_units,
            step=1,
            disabled=max_attack_units < 2)
        if st.button("Angriff!", type="primary"):
            throw_dice(attack_with)
            st.rerun()
        if st.button("Alles oder nichts!", help="Kämpfe bis eine Seite alle Einheiten verloren hat. Es werden die maximal möglichen Einheiten für Angriff und Verteidigung eingesetzt."):
            while(st.session_state.attack_units > 1 and st.session_state.defend_units > 0):
                throw_dice(min(3, st.session_state.attack_units-1))
            st.rerun()
    for log in reversed(st.session_state.log):
        st.markdown(log)