package com.sidev.agenda.resource.dto;

import com.sidev.agenda.model.EventCategory;
import jakarta.json.bind.annotation.JsonbCreator;
import jakarta.json.bind.annotation.JsonbProperty;

import java.time.LocalDateTime;

/**
 * DTO d'entree (corps de POST /api/calendrier/evenements). Le {@code @JsonbCreator}
 * est necessaire pour que Yasson desserialise correctement un record en mode
 * module-path strict (meme constat que Todo dans l'exemple officiel Vidocq :
 * sans lui, les champs restent silencieusement a leur valeur par defaut).
 */
public record CreateEventRequest(String title, LocalDateTime start, LocalDateTime end, EventCategory category) {

    @JsonbCreator
    public static CreateEventRequest create(@JsonbProperty("title") String title,
                                             @JsonbProperty("start") LocalDateTime start,
                                             @JsonbProperty("end") LocalDateTime end,
                                             @JsonbProperty("category") EventCategory category) {
        return new CreateEventRequest(title, start, end, category);
    }
}
