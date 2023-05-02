from flask import render_template, request, url_for, redirect, flash, session
from app.card_score import bp
from app.extensions import db
from app.models.card_score import CardScore
from shutil import copy
import os
import urllib


@bp.route('/', methods=('GET', 'POST'))
def index():
    query_players = CardScore.query.all()
    if len(query_players) > 0:
        CardScore.query.delete()
        db.session.commit()
    if request.method == "POST":
        print(request.form)
        no_players = request.form.get('no_players')
        if no_players is not None:
            CardScore.query.delete()
            db.session.commit()
            try:
                os.remove(r"app\templates\card_score\new_round.html")
            except:
                pass
            return render_template('card_score/enter_players.html', no_players=int(no_players))
        else:
            list_players = request.form
            no_players = len(list_players) // 2
            players = {'name': [], 'score': []}
            for p in range(no_players):
                name = list_players.get(f'name{p}')
                score = list_players.get(f'score{p}')
                players['name'].append(name)
                players['score'].append(score)
            
            existed_name = []
            for p in range(no_players):
                name = players['name'][p]
                score = players['score'][p]
                if name in existed_name:
                    flash(f"ERROR INPUT: There are two of the same names!", "error")
                    CardScore.query.delete()
                    db.session.commit()
                    return render_template('card_score/enter_players.html', no_players=int(no_players), players=players)
                elif len(score) == 0:
                    flash(f"ERROR INPUT: Miss starting score!", "error")
                    CardScore.query.delete()
                    db.session.commit()
                    return render_template('card_score/enter_players.html', no_players=int(no_players), players=players)
                else:
                    existed_name.append(name)
                    new_rows = CardScore(name=name, score=score, round=0)
                    db.session.add(new_rows)
                    db.session.commit()
            return redirect(url_for('card_score.ingame'))
    return render_template('card_score/index.html')


@bp.route('/ingame', methods=('GET', 'POST'))
def ingame():
    query_players = CardScore.query.all()
    players = [(q.name, q.score, q.round) for q in query_players]
    if request.method == 'POST':     
        res = "\n<tr>\n"
        res += f"<th>{players[0][2] + 1}</th>\n"
        check_score = 0
        for i in range(len(players)):
            try:
                check_score += int(request.form[f'score{i}'])
            except:
                flash("Error input! Score must be a number! Please enter again!")
                try:
                    return render_template('card_score/new_round.html', players=players, round=players[0][2] + 1)
                except:
                    return render_template('card_score/ingame.html', players=players, round=1)
        if check_score != 0:
            flash("Sum of score is not equal 0! Please enter again!", "error")
            try:
                return render_template('card_score/new_round.html', players=players, round=players[0][2] + 1)
            except:
                return render_template('card_score/ingame.html', players=players, round=1)
        else:
            for i in range(len(players)):
                score = request.form[f'score{i}']
                print(i, score)
                player = CardScore.query.filter_by(name=players[i][0]).first()
                print(player)
                player.score += int(score)
                player.round += 1
                db.session.commit()
                res += f"<th> {score} </th>\n"
            res += "</tr>\n"
            new_round_path = r'app\templates\card_score\new_round.html'
            if not os.path.isfile(new_round_path):
                copy(r'app\static\card_score\new_round.html', new_round_path)
            with open(new_round_path, 'r') as rf:
                read_file = rf.read()
            read_file =read_file.replace("{% endblock %}", res + "{% endblock %}")
            with open(new_round_path, 'w') as wf:
                wf.write(read_file)
            query_players = CardScore.query.all()
            players = [(q.name, q.score, q.round) for q in query_players]
            return redirect(url_for('card_score.ingame'))
            # return render_template('card_score/new_round.html', players=players, round=players[0][2] + 1)
    try:
        return render_template('card_score/new_round.html', players=players, round=players[0][2] + 1)
    except:
        return render_template('card_score/ingame.html', players=players, round=1)

@bp.route('/reset', methods=('GET', 'POST'))
def reset():
    CardScore.query.delete()
    db.session.commit()
    return redirect(url_for('card_score.index'))
