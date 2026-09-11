import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [cargoQuantity, setCargoQuantity] = useState(50000);
  const [origin, setOrigin] = useState("Australia");
  const [destination, setDestination] = useState("Dhamra");
  const [contractPreference, setContractPreference] =
    useState("Let system optimize");

  const analyzeVoyage = async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        cargo_quantity: cargoQuantity,
        origin: origin,
        destination: destination,
      });

      const response = await fetch(
        `http://127.0.0.1:8000/api/decision?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      setData(result);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to backend.");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    analyzeVoyage();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>SAIL Freight Intelligence</h1>
          <p>Chartering & Bulk Cargo Decision Support</p>
        </div>

        <div className="status">
          <span></span>
          ENGINE ONLINE
        </div>
      </header>

      <main>
        {/* PROCUREMENT INPUT */}

        <section className="panel input-panel">
          <div className="input-header">
            <div>
              <h2>Procurement Requirement</h2>
              <p>
                Define the cargo requirement and trade route.
                The engine determines the optimal strategy.
              </p>
            </div>
          </div>

          <div className="input-grid">
            <div className="input-group">
              <label>CARGO QUANTITY</label>

              <input
                type="number"
                min="1"
                value={cargoQuantity}
                onChange={(e) =>
                  setCargoQuantity(Number(e.target.value))
                }
              />

              <small>Tonnes</small>
            </div>

            <div className="input-group">
              <label>ORIGIN</label>

              <select
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
              >
                <option value="Australia">Australia</option>

                <option value="USA" disabled>
                  USA — coming soon
                </option>

                <option value="Mozambique" disabled>
                  Mozambique — coming soon
                </option>

                <option value="Russia" disabled>
                  Russia — coming soon
                </option>

                <option value="Indonesia" disabled>
                  Indonesia — coming soon
                </option>
              </select>

              <small>Loading region</small>
            </div>

            <div className="input-group">
              <label>DESTINATION</label>

              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
              >
                <option value="Dhamra">Dhamra</option>
                <option value="Paradip">Paradip</option>
                <option value="Visakhapatnam">
                  Visakhapatnam
                </option>
                <option value="Gangavaram">
                  Gangavaram
                </option>
                <option value="Gopalpur">Gopalpur</option>
                <option value="Sagar-Sandheads">
                  Sagar-Sandheads
                </option>
                <option value="Haldia">Haldia</option>
              </select>

              <small>East Coast India</small>
            </div>

            <div className="input-group">
              <label>CONTRACT CONSTRAINT</label>

              <select
                value={contractPreference}
                onChange={(e) =>
                  setContractPreference(e.target.value)
                }
              >
                <option value="Let system optimize">
                  Let system optimize
                </option>

                <option value="Spot">
                  Spot only
                </option>

                <option value="Short Term">
                  Short-term only
                </option>

                <option value="Medium Term">
                  Medium-term only
                </option>
              </select>

              <small>
                Optional procurement constraint
              </small>
            </div>
          </div>

          <button
            className="analyze-button"
            onClick={analyzeVoyage}
            disabled={loading}
          >
            {loading
              ? "ANALYZING REQUIREMENT..."
              : "ANALYZE REQUIREMENT"}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </section>

        {data && (
          <>
            {/* FINAL DECISION */}

            <section className="panel final-decision">
              <div>
                <label>FINAL PROCUREMENT STRATEGY</label>

                <h2>{data.recommendation}</h2>

                <p>
                  {data.best_vessel.vessel} ·{" "}
                  {data.best_vessel.class}
                </p>
              </div>

              <div className="final-cost">
                <span>ESTIMATED LOGISTICS COST</span>

                <strong>
                  $
                  {data.best_vessel.total_cost.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </strong>

                <small>
                  ${data.best_vessel.cost_per_tonne.toFixed(2)} / tonne
                </small>
              </div>
            </section>

            {/* CARGO SUMMARY */}

            <section className="cargo-card">
              <div>
                <label>CARGO</label>

                <h2>
                  {data.cargo.quantity.toLocaleString()} tonnes
                </h2>
              </div>

              <div>
                <label>ROUTE</label>

                <h2>
                  {data.cargo.origin} → {data.cargo.destination}
                </h2>
              </div>

              <div>
                <label>DISTANCE</label>

                <h2>
                  {data.route.distance_nm.toLocaleString()} nm
                </h2>
              </div>

              <div>
                <label>CONTRACT STRATEGY</label>

                <h2>
                  {data.contract_strategy.recommendation}
                </h2>
              </div>
            </section>

            {/* MARKET METRICS */}

            <section className="metrics">
              <div className="metric">
                <label>CURRENT FREIGHT</label>

                <strong>
                  ${data.forecast.current.toFixed(2)}
                </strong>

                <small>per tonne</small>
              </div>

              <div className="metric">
                <label>7-DAY FORECAST</label>

                <strong>
                  ${data.forecast.day_7.toFixed(2)}
                </strong>

                <small>per tonne</small>
              </div>

              <div className="metric">
                <label>14-DAY FORECAST</label>

                <strong>
                  ${data.forecast.day_14.toFixed(2)}
                </strong>

                <small>per tonne</small>
              </div>

              <div className="metric recommendation">
                <label>CHARTER TIMING</label>

                <strong>
                  {data.timing.recommendation}
                </strong>

                <small>system recommendation</small>
              </div>
            </section>

            {/* VESSEL INTELLIGENCE */}

            <section className="grid">

              {/* SELECTED VESSEL */}

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Vessel Intelligence</h2>

                    <p>
                      System-selected vessel based on feasibility,
                      voyage economics and freight risk
                    </p>
                  </div>

                  <strong>OPTIMAL VESSEL</strong>
                </div>

                <div className="best-vessel">
                  <div>
                    <h3>
                      {data.best_vessel.vessel}
                    </h3>

                    <p>
                      {data.best_vessel.class}
                    </p>
                  </div>

                  <div className="price">
                    <strong>
                      $
                      {data.best_vessel.risk_adjusted_cost_per_tonne.toFixed(
                        2
                      )}
                    </strong>

                    <small>
                      / tonne risk-adjusted
                    </small>
                  </div>
                </div>

                <div className="vessel-details">

                  <div>
                    <span>DWT</span>

                    <strong>
                      {data.best_vessel.dwt.toLocaleString()} t
                    </strong>
                  </div>

                  <div>
                    <span>VOYAGE</span>

                    <strong>
                      {data.best_vessel.voyage_days} days
                    </strong>
                  </div>

                  <div>
                    <span>FREIGHT</span>

                    <strong>
                      ${data.best_vessel.current_rate.toFixed(2)}/t
                    </strong>
                  </div>

                  <div>
                    <span>RISK-ADJUSTED</span>

                    <strong>
                      $
                      {data.best_vessel.risk_adjusted_cost.toLocaleString(
                        "en-US",
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }
                      )}
                    </strong>
                  </div>

                </div>

                <div className="selection-basis">
                  <h3>Selection Basis</h3>

                  <ul>
                    {data.vessel_selection.selection_basis.map(
                      (reason, index) => (
                        <li key={index}>
                          ✓ {reason}
                        </li>
                      )
                    )}
                  </ul>
                  <div className="vessel-comparison">
                    <h3>Next Best Feasible Vessel</h3>

                    {(() => {
                      const nextBest = data.vessel_analysis
                        .filter((v) => v.vessel !== data.best_vessel.vessel)
                        .sort(
                          (a, b) =>
                            a.risk_adjusted_cost_per_tonne -
                            b.risk_adjusted_cost_per_tonne
                        )[0];

                      if (!nextBest) return null;

                      const difference =
                        nextBest.risk_adjusted_cost_per_tonne -
                        data.best_vessel.risk_adjusted_cost_per_tonne;

                      return (
                        <div className="comparison-row">
                          <div>
                            <strong>{nextBest.vessel}</strong>
                            <span>{nextBest.class}</span>
                          </div>

                          <div className="comparison-price">
                            <strong>
                              ${nextBest.risk_adjusted_cost_per_tonne.toFixed(2)}/t
                            </strong>

                            <small>
                              ${difference.toFixed(2)}/t higher
                            </small>
                          </div>
                        </div>
                      );
                    })()}
                  </div>

                  <p>
                    {data.vessel_selection.explanation}
                  </p>
                </div>
              </div>

              {/* FEASIBLE VESSELS */}

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <h2>Feasible Vessels</h2>

                    <p>
                      Vessels satisfying cargo and port constraints
                    </p>
                  </div>

                  <strong>
                    {data.vessel_analysis.length} OPTIONS
                  </strong>
                </div>

                <div className="vessel-list">

                  {data.vessel_analysis.map((vessel) => (
                    <div
                      className="vessel-row"
                      key={vessel.vessel}
                    >
                      <div>
                        <strong>
                          {vessel.vessel}
                        </strong>

                        <span>
                          {vessel.class}
                        </span>
                      </div>

                      <div>
                        <strong>
                          ${vessel.risk_adjusted_cost_per_tonne.toFixed(2)}
                        </strong>

                        <span>
                          /t risk-adjusted
                        </span>
                      </div>
                    </div>
                  ))}

                </div>
              </div>

            </section>

            {/* REJECTED VESSELS */}

            {data.rejected_vessels &&
              data.rejected_vessels.length > 0 && (
                <section className="panel">

                  <div className="panel-header">
                    <div>
                      <h2>Rejected Vessels</h2>

                      <p>
                        Vessels excluded by operational or cargo constraints
                      </p>
                    </div>

                    <strong>
                      {data.rejected_vessels.length} REJECTED
                    </strong>
                  </div>

                  <div className="vessel-list">

                    {data.rejected_vessels.map(
                      (vessel) => (
                        <div
                          className="vessel-row"
                          key={vessel.vessel}
                        >
                          <div>
                            <strong>
                              {vessel.vessel}
                            </strong>

                            <span>
                              {vessel.class}
                            </span>
                          </div>

                          <div>
                            {vessel.reasons.map(
                              (reason, index) => (
                                <span
                                  key={index}
                                  style={{
                                    display: "block",
                                  }}
                                >
                                  ✕ {reason}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )
                    )}

                  </div>
                </section>
              )}

            {/* PORT INTELLIGENCE */}

            <section className="panel">

              <div className="panel-header">
                <div>
                  <h2>Port Intelligence</h2>

                  <p>
                    Destination infrastructure and operational constraints
                  </p>
                </div>
              </div>

              <div className="vessel-details">

                <div>
                  <span>MAX DRAFT</span>

                  <strong>
                    {data.port.max_draft} m
                  </strong>
                </div>

                <div>
                  <span>MAX LOA</span>

                  <strong>
                    {data.port.max_loa} m
                  </strong>
                </div>

                <div>
                  <span>MAX BEAM</span>

                  <strong>
                    {data.port.max_beam} m
                  </strong>
                </div>

                <div>
                  <span>HANDLING</span>

                  <strong>
                    {data.port.handling_rate.toLocaleString()}
                  </strong>
                </div>

                <div>
                  <span>CONGESTION</span>

                  <strong>
                    {(data.port.congestion * 100).toFixed(0)}%
                  </strong>
                </div>

                <div>
                  <span>WAITING</span>

                  <strong>
                    {data.port.waiting_days} days
                  </strong>
                </div>

              </div>
              <div className="port-fit">
                <h3>Selected Vessel Compatibility</h3>

                <div className="port-fit-grid">
                  <div>
                    <span>DRAFT</span>
                    <strong>{data.best_vessel.draft} m</strong>
                    <small>Limit: {data.port.max_draft} m ✓</small>
                  </div>

                  <div>
                    <span>LOA</span>
                    <strong>{data.best_vessel.loa} m</strong>
                    <small>Limit: {data.port.max_loa} m ✓</small>
                  </div>

                  <div>
                    <span>BEAM</span>
                    <strong>{data.best_vessel.beam} m</strong>
                    <small>Limit: {data.port.max_beam} m ✓</small>
                  </div>
                </div>

                <div className="port-fit-status">
                  ✓ SELECTED VESSEL FITS DESTINATION PORT
                </div>
              </div>
            </section>

            {/* FREIGHT FORECAST */}

            <section className="panel forecast-panel">

              <div className="panel-header">

                <div>
                  <h2>Freight Forecast</h2>

                  <p>
                    30-day XGBoost prediction ·{" "}
                    {data.forecast.vessel_class}
                  </p>
                </div>

                <div className="forecast-values">

                  <span>
                    Current $
                    {data.forecast.current.toFixed(2)}
                  </span>

                  <span>
                    30D $
                    {data.forecast.day_30.toFixed(2)}
                  </span>

                </div>

              </div>

              <div className="forecast-chart">

                <svg
                  viewBox="0 0 800 240"
                  preserveAspectRatio="none"
                  className="chart"
                >

                  <line
                    x1="0"
                    y1="40"
                    x2="800"
                    y2="40"
                    className="grid-line"
                  />

                  <line
                    x1="0"
                    y1="120"
                    x2="800"
                    y2="120"
                    className="grid-line"
                  />

                  <line
                    x1="0"
                    y1="200"
                    x2="800"
                    y2="200"
                    className="grid-line"
                  />

                  <polyline
                    points={data.forecast.full
                      .map((point, index) => {

                        const values =
                          data.forecast.full.map(
                            (item) => item.forecast
                          );

                        const min =
                          Math.min(...values) - 0.2;

                        const max =
                          Math.max(...values) + 0.2;

                        const x =
                          (index /
                            (values.length - 1)) *
                          800;

                        const y =
                          220 -
                          ((point.forecast - min) /
                            (max - min)) *
                          200;

                        return `${x},${y}`;
                      })
                      .join(" ")}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                  />

                </svg>

              </div>

              <div className="chart-labels">
                <span>Today</span>
                <span>Day 7</span>
                <span>Day 14</span>
                <span>Day 21</span>
                <span>Day 30</span>
              </div>
              <div className="forecast-outlook">
                <div>
                  <span>EXPECTED 30-DAY CHANGE</span>

                  <strong>
                    {(
                      ((data.forecast.day_30 - data.forecast.current) /
                        data.forecast.current) *
                      100
                    ).toFixed(1)}
                    %
                  </strong>
                </div>

                <div>
                  <span>MARKET OUTLOOK</span>

                  <strong>
                    {data.forecast.day_30 > data.forecast.current
                      ? "↗ Upward pressure"
                      : data.forecast.day_30 < data.forecast.current
                        ? "↘ Downward pressure"
                        : "→ Stable market"}
                  </strong>
                </div>
              </div>

            </section>

            {/* CHARTER TIMING */}

            <section className="panel timing-panel">

              <div className="panel-header">

                <div>
                  <h2>Charter Timing Analysis</h2>

                  <p>
                    Compare estimated voyage cost across procurement timing scenarios
                  </p>
                </div>

                <strong>
                  {data.timing.recommendation}
                </strong>

              </div>

              <div className="timing-grid">

                <div>
                  <span>CHARTER NOW</span>

                  <strong>
                    $
                    {data.scenarios.current.total_cost.toLocaleString(
                      "en-US",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </strong>

                  <small>
                    $
                    {data.scenarios.current.cost_per_tonne.toFixed(2)}
                    {" "} / tonne
                  </small>
                </div>

                <div>
                  <span>WAIT 7 DAYS</span>

                  <strong>
                    $
                    {data.scenarios.wait_7.total_cost.toLocaleString(
                      "en-US",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </strong>

                  <small>
                    Saving: $
                    {data.scenarios.wait_7.estimated_saving.toLocaleString(
                      "en-US"
                    )}
                  </small>

                  <small>
                    {data.scenarios.wait_7.probability_wait_cheaper.toFixed(
                      1
                    )}
                    % chance cheaper
                  </small>
                </div>

                <div>
                  <span>WAIT 14 DAYS</span>

                  <strong>
                    $
                    {data.scenarios.wait_14.total_cost.toLocaleString(
                      "en-US",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </strong>

                  <small>
                    Saving: $
                    {data.scenarios.wait_14.estimated_saving.toLocaleString(
                      "en-US"
                    )}
                  </small>

                  <small>
                    {data.scenarios.wait_14.probability_wait_cheaper.toFixed(
                      1
                    )}
                    % chance cheaper
                  </small>
                </div>

              </div>
            </section>

            {/* CONTRACT STRATEGY */}

            <section className="panel">

              <div className="panel-header">

                <div>
                  <h2>Contract Strategy</h2>

                  <p>
                    System-generated procurement strategy
                  </p>
                </div>

                <strong>
                  {data.contract_strategy.recommendation}
                </strong>

              </div>

              <div className="timing-grid">

                <div>
                  <span>SPOT</span>

                  <strong>
                    $
                    {data.contract_strategy.strategies.spot.rate_per_tonne.toFixed(
                      2
                    )}
                    /t
                  </strong>

                  <small>
                    1 voyage
                  </small>
                </div>

                <div>
                  <span>SHORT TERM</span>

                  <strong>
                    $
                    {data.contract_strategy.strategies.short_term.rate_per_tonne.toFixed(
                      2
                    )}
                    /t
                  </strong>

                  <small>
                    4 voyages
                  </small>
                </div>

                <div>
                  <span>MEDIUM TERM</span>

                  <strong>
                    $
                    {data.contract_strategy.strategies.medium_term.rate_per_tonne.toFixed(
                      2
                    )}
                    /t
                  </strong>

                  <small>
                    8 voyages
                  </small>
                </div>

              </div>

              <p>
                {data.contract_strategy.explanation}
              </p>

              <div className="contract-insight">
                <span>PROCUREMENT INSIGHT</span>

                <strong>
                  {data.contract_strategy.recommendation === "SPOT"
                    ? "Spot charter is currently preferred"
                    : data.contract_strategy.recommendation ===
                      "SHORT-TERM MULTIPLE VOYAGE"
                      ? "Short-term multiple voyages are currently preferred"
                      : "Medium-term multiple voyages are currently preferred"}
                </strong>

                <p>
                  The system compares expected freight economics and market
                  volatility before selecting the procurement strategy.
                </p>
              </div>
            </section>

            {/* EXPLANATION */}

            <section className="panel explanation">

              <h2>Why this decision?</h2>

              <p>
                {data.explanation}
              </p>

            </section>

          </>
        )}
      </main>
    </div>
  );
}

export default App;