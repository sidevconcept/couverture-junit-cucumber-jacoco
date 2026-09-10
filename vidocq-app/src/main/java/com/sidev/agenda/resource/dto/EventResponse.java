package com.sidev.agenda.resource.dto;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;

import java.time.LocalDateTime;

/**
 * DTO de sortie. L'id est expose en String (UUID.toString()) plutot qu'en
 * UUID brut : JSON-B/Yasson n'a pas d'adaptateur par defaut pour java.util.UUID,
 * il le serialiserait comme un objet {mostSigBits, leastSigBits} au lieu d'une
 * simple chaine — on evite le probleme plutot que d'ecrire un JsonbAdapter dedie.
 */
public record EventResponse(String id, String title, LocalDateTime start, LocalDateTime end, EventCategory category) {

    public static EventResponse from(Event event) {
        return new EventResponse(event.id().toString(), event.title(), event.start(), event.end(), event.category());
    }
}
