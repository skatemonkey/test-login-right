from pydantic import BaseModel, Field


class LineChartHistoryRequest(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    series: list[str] = Field(min_length=1)


class LineChartPoint(BaseModel):
    x: int
    y: float


class LineChartSeries(BaseModel):
    name: str
    data: list[LineChartPoint]


class LineChartHistoryResponse(BaseModel):
    series: list[LineChartSeries]


class LineChartStreamQuery(BaseModel):
    series: str | None = None


class LineChartSsePoint(BaseModel):
    series: str
    timestamp: int
    value: float
