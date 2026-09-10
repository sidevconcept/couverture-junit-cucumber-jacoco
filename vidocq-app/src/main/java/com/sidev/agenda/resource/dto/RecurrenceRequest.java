package com.sidev.agenda.resource.dto;

import com.sidev.agenda.service.RecurrenceFrequency;
import jakarta.json.bind.annotation.JsonbCreator;
import jakarta.json.bind.annotation.JsonbProperty;

public record RecurrenceRequest(RecurrenceFrequency frequency, int occurrences) {

    @JsonbCreator
    public static RecurrenceRequest create(@JsonbProperty("frequency") RecurrenceFrequency frequency,
                                            @JsonbProperty("occurrences") int occurrences) {
        return new RecurrenceRequest(frequency, occurrences);
    }
}
