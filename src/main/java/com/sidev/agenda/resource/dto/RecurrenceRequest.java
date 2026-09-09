package com.sidev.agenda.resource.dto;

import com.sidev.agenda.service.RecurrenceFrequency;

public record RecurrenceRequest(RecurrenceFrequency frequency, int occurrences) {
}
