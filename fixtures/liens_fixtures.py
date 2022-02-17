from models import Joueur

liens = [
    Joueur(reunion_id=1, copain_id=1, est_guest=False, dette_active=False, dette=100),
    Joueur(reunion_id=1, copain_id=2, est_guest=False, dette_active=True, dette=210),
    Joueur(reunion_id=1, copain_id=3, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=1, copain_id=4, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=1, copain_id=5, est_guest=True, dette_active=False, dette=0),
    Joueur(reunion_id=2, copain_id=1, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=2, copain_id=2, est_guest=False, dette_active=True, dette=150),
    Joueur(reunion_id=2, copain_id=3, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=2, copain_id=4, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=2, copain_id=5, est_guest=True, dette_active=False, dette=0),
    Joueur(reunion_id=3, copain_id=1, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=3, copain_id=2, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=3, copain_id=3, est_guest=False, dette_active=False, dette=0),
    Joueur(reunion_id=3, copain_id=4, est_guest=False, dette_active=False, dette=0),
]
