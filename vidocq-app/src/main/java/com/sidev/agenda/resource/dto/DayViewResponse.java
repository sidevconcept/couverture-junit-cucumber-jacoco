package com.sidev.agenda.resource.dto;

import java.time.LocalDate;
import java.util.List;

public record DayViewResponse(LocalDate date, List<EventResponse> events, String holidayGreeting, String quoteOfTheDay) {
}
