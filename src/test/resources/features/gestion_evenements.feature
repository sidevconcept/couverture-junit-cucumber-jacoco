# language: fr
Fonctionnalité: Gestion des évenements de l'agenda
  En tant qu'utilisatrice de l'agenda
  Je veux créer des évenements et consulter ma journée
  Afin d'organiser mon emploi du temps sans double-réservation

  Scénario: Création d'un événement dans un créneau libre
    Étant donné que mon agenda est vide pour le "2026-09-14"
    Quand je crée l'événement "Atelier tests" de "09:00" à "10:30" le "2026-09-14"
    Alors l'événement "Atelier tests" apparait dans ma journée du "2026-09-14"

  Scénario: Refus d'un événement qui chevauche un événement existant
    Étant donné que j'ai déjà l'événement "Comité de pilotage" de "14:00" à "15:00" le "2026-09-15"
    Quand je crée l'événement "Revue de code" de "14:30" à "15:30" le "2026-09-15"
    Alors la création est refusée pour cause de conflit d'horaire

  Scénario: Un jour férié est signalé dans la vue du jour
    Quand je consulte ma journée du "2026-12-25"
    Alors le message de jour férié est présent dans la réponse
