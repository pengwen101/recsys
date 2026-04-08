import { useState } from 'react';
import api from './api/axios';

function App() {
  const [view, setView] = useState('search');
  const [userIdInput, setUserIdInput] = useState('');
  const [selectedUser, setSelectedUser] = useState('');

  const [recommendations, setRecommendations] = useState([]);

  const [popularMovies, setPopularMovies] = useState([]);
  const [pickedMovies, setPickedMovies] = useState([]);
  const [groupedRecommendations, setGroupedRecommendations] = useState([]);

  const [selectedMovie, setSelectedMovie] = useState(null);
  const [similarMovies, setSimilarMovies] = useState([]);

  const [loading, setLoading] = useState(false);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!userIdInput) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/recommend/user/${userIdInput}`);
      setRecommendations(response.data.recommendations || []);
      setGroupedRecommendations([]);
      setSelectedUser(userIdInput);
      setView('results');
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError(`User ID ${userIdInput} not found in the database.`);
      } else {
        console.error("Failed to fetch recommendations:", err);
        setError("An error occurred while fetching recommendations.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNewUser = async () => {
    setLoading(true);
    setError(null);
    setUserIdInput('');

    try {
      const response = await api.get('/recommend/popular', { params: { k: 10 } });
      setPopularMovies(response.data.recommendations || []);
      setPickedMovies([]);
      setView('picking');
    } catch (err) {
      console.error("Failed to fetch popular movies:", err);
      setError("Failed to load popular movies. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const togglePick = (movie) => {
    const isPicked = pickedMovies.some(m => m.movie_id === movie.movie_id);
    if (isPicked) {
      setPickedMovies(pickedMovies.filter(m => m.movie_id !== movie.movie_id));
    } else {
      if (pickedMovies.length < 3) {
        setPickedMovies([...pickedMovies, movie]);
      }
    }
  };

  const submitPicks = async () => {
    setLoading(true);
    setError(null);

    try {
      const promises = pickedMovies.map(m => 
        api.get(`/recommend/similar/${m.movie_id}`, { params: { k: 10 } })
      );
      
      const responses = await Promise.all(promises);
    
      const grouped = responses.map((res, index) => {
        const sourceMovie = pickedMovies[index];
        const recs = res.data.recommendations || [];
      
        const enrichedRecs = recs.map(r => ({
          ...r,
          reason: r.reason || `Because you liked ${sourceMovie.title}`
        }));

        return {
          sourceMovie: sourceMovie,
          recommendations: enrichedRecs
        };
      });

      setGroupedRecommendations(grouped);
      setRecommendations([]);
      setSelectedUser('New User');
      setView('results');
    } catch (err) {
      console.error("Failed to fetch similar movies:", err);
      setError("Failed to generate your personalized recommendations.");
    } finally {
      setLoading(false);
    }
  };

  const viewMovieDetails = async (movie) => {
    setSelectedMovie(movie);
    setView('details');
    setLoadingSimilar(true);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
      const response = await api.get(`/recommend/similar/${movie.movie_id}`, { params: { k: 5 } });
      setSimilarMovies(response.data.recommendations || []);
    } catch (err) {
      console.error("Failed to fetch similar movies:", err);
    } finally {
      setLoadingSimilar(false);
    }
  };

  const resetApp = () => {
    setView('search');
    setUserIdInput('');
    setError(null);
    setSelectedMovie(null);
  };

  const MovieCard = ({ rec, onClick, selectable, isSelected, hideMeta = false }) => {
    const { movie, score, reason } = rec;
    return (
      <div 
        onClick={() => onClick(movie)}
        className={`bg-neutral-900 rounded-2xl border ${
          isSelected ? 'border-red-500 shadow-lg shadow-red-500/20' : 'border-neutral-800 hover:border-neutral-600'
        } transition-all p-4 flex flex-col h-full group cursor-pointer relative overflow-hidden`}
      >
        <div className="aspect-[2/3] w-full bg-neutral-950 rounded-xl overflow-hidden mb-4 relative flex-shrink-0">
          {movie.poster_url && movie.poster_url !== "None" && movie.poster_url !== "" ? (
            <img src={movie.poster_url} alt={movie.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          ) : (
            <div className="flex items-center justify-center w-full h-full text-neutral-700 text-sm">No Poster</div>
          )}
          
          {selectable && isSelected && (
            <div className="absolute top-2 right-2 h-8 w-8 bg-red-600 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
        </div>

        <h3 className="text-lg font-bold text-white mb-1 group-hover:text-red-500 transition-colors line-clamp-1">
          {movie.title}
        </h3>
        <p className="text-xs text-neutral-400 mb-3 flex-grow line-clamp-2">
          {movie.genres?.join(' • ')}
        </p>

        {!hideMeta && (
          <div className="mt-auto space-y-2">
            {reason && (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium bg-neutral-950 border border-neutral-800 text-neutral-300 w-full">
                <span className="truncate">{reason}</span>
              </div>
            )}
            {score !== undefined && (
              <div>
                <span className="inline-block px-2 py-0.5 rounded bg-red-950/30 text-[11px] font-bold text-red-500">
                  Match: {(score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-neutral-950 py-8 px-4 sm:px-6 lg:px-8 font-sans text-gray-100 selection:bg-red-500/30">
      <div className="max-w-7xl mx-auto">
        
        <h1 
          className="text-4xl md:text-5xl font-black text-center tracking-tight mb-12 cursor-pointer transition-transform hover:scale-105"
          onClick={resetApp}
        >
          <span className="text-white">MOVIE</span>
          <span className="text-red-600">RECS</span>
        </h1>

        {error && (
          <div className="max-w-2xl mx-auto bg-red-950/50 border border-red-500/50 text-red-400 p-4 mb-8 rounded-xl text-center">
            <p className="font-medium">{error}</p>
          </div>
        )}
        {loading && (
          <div className="flex justify-center items-center mb-8 h-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
          </div>
        )}

        {view === 'search' && !loading && (
          <div className="max-w-md mx-auto space-y-8 animate-in fade-in zoom-in duration-500">
            <div className="bg-neutral-900 p-8 rounded-3xl shadow-xl border border-neutral-800">
              <h2 className="text-xl font-bold text-white mb-6">Welcome Back</h2>
              <form onSubmit={handleSearch} className="space-y-4">
                <input 
                  type="number"
                  value={userIdInput}
                  onChange={(e) => setUserIdInput(e.target.value)}
                  placeholder="Enter User ID (e.g., 42)"
                  className="w-full px-5 py-3.5 bg-neutral-950 border border-neutral-800 rounded-xl text-white focus:ring-2 focus:ring-red-600 outline-none transition-all"
                />
                <button type="submit" disabled={!userIdInput} className="w-full py-3.5 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold rounded-xl transition-all active:scale-[0.98]">
                  Log In
                </button>
              </form>
            </div>
            <button onClick={handleNewUser} className="w-full py-4 bg-neutral-900 hover:bg-neutral-800 border border-neutral-700 text-white font-bold rounded-xl transition-all">
              I'm a New User
            </button>
          </div>
        )}

        {view === 'picking' && !loading && (
          <section className="animate-in fade-in slide-in-from-bottom-8 duration-500 pb-24">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-white">Pick 3 Movies You Love</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {popularMovies.map((rec) => (
                <MovieCard 
                  key={rec.movie.movie_id} 
                  rec={rec} 
                  onClick={() => togglePick(rec.movie)}
                  selectable={true}
                  isSelected={pickedMovies.some(m => m.movie_id === rec.movie.movie_id)}
                  hideMeta={true}
                />
              ))}
            </div>

            <div className="fixed bottom-0 left-0 w-full bg-neutral-950/90 backdrop-blur-md border-t border-neutral-800 p-4 z-50">
              <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div>
                  <span className="text-neutral-400 font-medium">Selected: </span>
                  <span className={`text-xl font-bold ${pickedMovies.length === 3 ? 'text-red-500' : 'text-white'}`}>{pickedMovies.length} / 3</span>
                </div>
                <button onClick={submitPicks} disabled={pickedMovies.length < 3} className="px-8 py-3 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold rounded-xl">
                  Get Recommendations
                </button>
              </div>
            </div>
          </section>
        )}

        {view === 'results' && !loading && (
          <section className="animate-in fade-in duration-500">
            <div className="flex justify-between items-end mb-8 border-b border-neutral-800 pb-4">
              <h2 className="text-2xl font-bold text-white">Top Picks for You</h2>
              <button onClick={resetApp} className="text-sm font-medium text-neutral-400 hover:text-white transition-colors border border-neutral-700 px-4 py-2 rounded-lg">
                Change User
              </button>
            </div>
       
            {selectedUser === 'New User' && groupedRecommendations.length > 0 && (
              <div className="space-y-12">
                {groupedRecommendations.map((group, index) => (
                  <div key={index} className="w-full">
                    <h3 className="text-xl font-bold text-white mb-4 pl-2 border-l-4 border-red-600">
                      Because you liked <span className="text-red-500">{group.sourceMovie.title}</span>
                    </h3>
        
                    <div 
                      className="flex overflow-x-auto gap-6 pb-6 snap-x snap-mandatory [&::-webkit-scrollbar]:hidden"
                      style={{ scrollbarWidth: 'none' }}
                    >
                      {group.recommendations.map((rec, idx) => (
                        <div key={`${rec.movie.movie_id}-${idx}`} className="w-[240px] md:w-[280px] flex-shrink-0 snap-start">
                          <MovieCard 
                            rec={rec} 
                            onClick={() => viewMovieDetails(rec.movie)} 
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {selectedUser !== 'New User' && recommendations.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {recommendations.map((rec, index) => (
                  <MovieCard 
                    key={`${rec.movie.movie_id}-${index}`} 
                    rec={rec} 
                    onClick={() => viewMovieDetails(rec.movie)} 
                  />
                ))}
              </div>
            )}
          </section>
        )}

        {view === 'details' && selectedMovie && (
          <section className="animate-in slide-in-from-right-8 duration-500">
            <button 
              onClick={() => setView('results')}
              className="mb-6 flex items-center text-neutral-400 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Results
            </button>

            <div className="bg-neutral-900 rounded-3xl border border-neutral-800 p-6 md:p-10 flex flex-col md:flex-row gap-8 mb-12">
              <div className="w-full md:w-1/3 lg:w-1/4 flex-shrink-0">
                <div className="aspect-[2/3] w-full bg-neutral-950 rounded-2xl overflow-hidden shadow-2xl shadow-red-900/10">
                  {selectedMovie.poster_url && selectedMovie.poster_url !== "None" ? (
                    <img src={selectedMovie.poster_url} alt={selectedMovie.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="flex items-center justify-center w-full h-full text-neutral-700">No Poster Available</div>
                  )}
                </div>
              </div>

              <div className="flex flex-col flex-grow">
                <h2 className="text-4xl font-black text-white mb-2">{selectedMovie.title}</h2>
                <p className="text-red-500 font-semibold mb-6 flex gap-2 flex-wrap">
                  {selectedMovie.genres?.map(g => (
                    <span key={g} className="px-3 py-1 bg-red-950/40 rounded-full text-xs">{g}</span>
                  ))}
                </p>

                <div className="mb-8">
                  <h4 className="text-sm font-bold text-neutral-500 uppercase tracking-wider mb-2">Overview</h4>
                  <p className="text-neutral-300 leading-relaxed text-lg">
                    {selectedMovie.overview || "No overview available."}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-auto">
                  <div>
                    <h4 className="text-sm font-bold text-neutral-500 uppercase tracking-wider mb-1">Director</h4>
                    <p className="text-white">
                      {selectedMovie.directors?.length > 0 
                        ? selectedMovie.directors.map(d => d.name).join(', ') 
                        : "Unknown"}
                    </p>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-neutral-500 uppercase tracking-wider mb-1">Top Cast</h4>
                    <p className="text-white">
                      {selectedMovie.casts?.length > 0 
                        ? selectedMovie.casts.map(c => c.name).join(', ') 
                        : "Unknown"}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t border-neutral-800 pt-10">
              <h3 className="text-2xl font-bold text-white mb-6 pl-2 border-l-4 border-neutral-600">
                If you liked this, you might also like...
              </h3>
              
              {loadingSimilar ? (
                 <div className="flex justify-center py-12">
                   <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
                 </div>
              ) : (
                <div 
                  className="flex overflow-x-auto gap-6 pb-6 snap-x snap-mandatory [&::-webkit-scrollbar]:hidden"
                  style={{ scrollbarWidth: 'none' }}
                >
                  {similarMovies.map((rec, index) => (
                    <div key={`sim-${rec.movie.movie_id}-${index}`} className="w-[240px] md:w-[280px] flex-shrink-0 snap-start">
                      <MovieCard 
                        rec={rec} 
                        onClick={() => viewMovieDetails(rec.movie)} 
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

export default App;