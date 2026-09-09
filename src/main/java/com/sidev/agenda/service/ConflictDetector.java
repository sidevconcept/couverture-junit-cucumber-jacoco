package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import jakarta.enterprise.context.ApplicationScoped;

/**
 * Detecte les chevauchements entre deux evenements du calendrier.
 */
@ApplicationScoped
public class ConflictDetector {

    /**
     * Deux evenements sont en conflit s'ils se chevauchent dans le temps.
     * Deux evenements qui se touchent exactement (l'un finit quand l'autre commence)
     * ne sont PAS consideres en conflit.
     */
    public boolean isConflicting(Event a, Event b) {
        if (a.id() != null && a.id().equals(b.id())) {
            return false;
        }
        return a.start().isBefore(b.end()) && b.start().isBefore(a.end());
    }
}
