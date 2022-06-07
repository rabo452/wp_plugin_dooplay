<?php
/*
Plugin Name: Adder plugin
Description: add the streaming link into dooplay theme and monitor the site for broken links
Version: 1.0
Author: dimka
*/
header("Access-Control-Allow-Origin: *");
header("Content-Type: text/html; charset=utf-8");
//here is import all need files
require_once (__DIR__ .'/../../../wp-load.php');
defined('ABSPATH') or die('here is an error');
require_once(ABSPATH . 'wp-admin/includes/media.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-config.php');
require_once(ABSPATH . 'wp-includes/wp-db.php');
require_once(ABSPATH . 'wp-admin/includes/taxonomy.php');
require_once(ABSPATH . 'wp-includes/class-wp-query.php');
$secret_key = 'SeCREt_kEy';




# for 3 program
if ($_POST['secret_key'] == $secret_key and isset($_POST['get_id_by_link']) and isset($_POST['link'])) {
  $answer = ['title' => 'null', 'season_num' => 'null', 'episode_num' => 'null'];
  $answer['id'] = (int) url_to_postid($_POST['link']);
  if ($answer['id'] == 0) $answer['id'] = 'null';
  else {
	$post_info = get_post($answer['id']);
	if ($post_info->post_type == 'episodes') {
	  $answer['title'] = get_post_meta($answer['id'], 'serie')[0];
	  $answer['season_num'] = (string) get_post_meta($answer['id'], 'temporada')[0];
	  $answer['episode_num'] = (string) get_post_meta($answer['id'], 'episodio')[0];
	}elseif ($post_info->post_type == 'movies') $answer['title'] = $post_info->post_title;


  }

  echo json_encode($answer);
  die();
}






// for monitor site 2 script change broken links by python program
// functionality for movies
if ($_POST['secret_key'] == $secret_key and isset($_POST['get_movies_info'])) {
  echo json_encode(get_movies_info());
}

if ($_POST['secret_key'] == $secret_key and isset($_POST['change_movie_stream_link']) and isset($_POST['movie_name']) and isset($_POST['movie_stream_links']) and isset($_POST['wordpress_post_id'])) {
  echo set_new_movie_stream_links((int) $_POST['wordpress_post_id'], $_POST['movie_name'], json_decode(stripslashes($_POST['movie_stream_links'])) );
}

function set_new_movie_stream_links($post_id, $movie_name, $stream_links) {
  array_splice($stream_links, 10);
  $post_meta = [];
  for($i=0;$i < count($stream_links); $i++) $post_meta[] = ['name' => "Player ". ($i + 1), 'select' => 'iframe', 'idioma' => 'es', 'url' => $stream_links[$i]];

  $post_id = duplicate_post((int) $post_id, $post_meta);
  return "Succesfully checked and updated the $movie_name ". get_permalink((int) $post_id);
}


# $post_meta - repeatable fields post meta
function duplicate_post($post_id, $post_meta) {
  $post_info = get_post($post_id);
  $meta_fields = get_post_meta($post_id, '');
  $meta_fields['repeatable_fields'] = [ $post_meta ];

  unset($post_info->ID);
  $post_info = json_decode(json_encode($post_info));

  #get the terms
  $director_ids = [];
  $terms_director = wp_get_object_terms($post_id,'dtdirector');
  for ($i = 0; $i < count($terms_director); $i++) $director_ids[] = $terms_director[$i]->term_id;
  $dtcast_ids = [];
  $term_dtcast = wp_get_object_terms($post_id,'dtcast');
  for ($i = 0; $i < count($term_dtcast); $i++) $dtcast_ids[] = $term_dtcast[$i]->term_id;
  $genre_ids = [];
  $term_genres = wp_get_object_terms($post_id,'genres');
  for ($i = 0; $i < count($term_genres); $i++) $genre_ids[] = $term_genres[$i]->term_id;


  wp_delete_post($post_id);
  $new_id = wp_insert_post($post_info);
  foreach($meta_fields as $meta_key => $meta_values)
	foreach($meta_values as $value)
	  add_post_meta($new_id,$meta_key,$value);

  #set the terms
  wp_set_object_terms($new_id, $director_ids,'dtdirector');
  wp_set_object_terms($new_id, $genre_ids,'genres');
  wp_set_object_terms($new_id, $dtcast_ids,'dtcast');




  wp_update_post(array('ID' => (int) $new_id));
  return $new_id;
}




function get_movies_info() {
  $result = [];

  $posts_count = (int) wp_count_posts('movies');
  for ($i=0;$i < ceil($posts_count / 5000); $i++) {
    $query = new WP_Query([ 'post_type' => 'movies', 'offset' => ($i * 5000), 'posts_per_page' => 5000 ]);
    while ($query->have_posts()) {
      $query->the_post();
	    $id = get_the_ID();
	    $stream_links_with_names = get_post_meta($id, 'repeatable_fields');
	    $stream_links = [];
	    foreach ($stream_links_with_names[0] as $stream_link) $stream_links[] = $stream_link['url'];
      $result[] = ['title' => get_the_title(), 'stream_links' => $stream_links, 'ID' => $id];
    }
    wp_reset_postdata();

  }

  return $result;
}








// functionality for tvshows
if ($_POST['secret_key'] == $secret_key and isset($_POST['get_tvshows_info'])) {
  echo json_encode(get_episodes_info());
}


function get_episodes_info() {
  $result = [];

  $posts_count = (int) wp_count_posts('episodes');
  for($i=0;$i < ceil($posts_count / 5000); $i++) {
    $query = new WP_Query([ 'post_type' => 'episodes', 'posts_per_page' => 5000, 'offset' => ($i * 5000) ]);
    while ($query->have_posts()) {
      $query->the_post();
  	  $id = get_the_ID();

  	  $serie_name = get_post_meta($id, 'serie');
  	  $serie_name = is_array($serie_name) ? $serie_name[0] : $serie_name;
  	  $serie_name = is_array($serie_name) ? $serie_name[0] : $serie_name;
  	  if (empty($serie_name)) continue;

  	  $episode_num = get_post_meta($id, 'episodio');
  	  $episode_num = is_array($episode_num) ? $episode_num[0] : $episode_num;
  	  $episode_num = is_array($episode_num) ? $episode_num[0] : $episode_num;
  	  $temporada_num = get_post_meta($id, 'temporada');
  	  $temporada_num = is_array($temporada_num) ? $temporada_num[0] : $temporada_num;
  	  $temporada_num = is_array($temporada_num) ? $temporada_num[0] : $temporada_num;

  	  $stream_links_with_names = get_post_meta($id, 'repeatable_fields');
  	  $stream_links = [];
  	  foreach ($stream_links_with_names[0] as $stream_link) $stream_links[] = $stream_link['url'];

      $result[] = ['title' => $serie_name, 'stream_links' => $stream_links, 'ID' => $id, 'season_num' => (string) $temporada_num, 'episode_num' => (string) $episode_num];
  	}
    wp_reset_postdata();
  }

  return $result;
}











//for 1 script
//save movies to wordpress functionality
if ($_POST['secret_key'] == $secret_key and isset($_POST['movie_name']) and isset($_POST['stream_links'])) {
  $movie_name = stripslashes($_POST['movie_name']);
  $movie_links = json_decode(stripslashes($_POST['stream_links']), true);
  add_to_wordpress_movie($movie_name, $movie_links);
}


function add_to_wordpress_movie($movie_name, $streaming_links) {
  //before adding check if the movie has already in wordpress
  $posts_titles = get_post_type_titles('movies');
  foreach($posts_titles as $post_title) if (str_replace(' ', '', strtolower($post_title)) == str_replace(' ', '', strtolower($movie_name))) return;

  //add to wordpress
  $post_id = wp_insert_post(array (
   'post_type' => 'movies',
   'post_title' => $movie_name,
   'post_content' => $movie_name,
   'post_status' => 'publish',
  ));

  $repeatable_fields = [];
  $i = 1;
  foreach($streaming_links as $stream_link) {
  	$repeatable_fields[] = ['name' => "Player $i", 'select' => 'iframe', 'idioma' => 'es', 'url' => $stream_link];
    $i++;
  }
  add_post_meta($post_id,'repeatable_fields', $repeatable_fields);
}







//save series to wordpress site
if ($_POST['secret_key'] == $secret_key and isset($_POST['stream_links_series']) and isset($_POST['series_name'])) {
  $stream_links = json_decode(stripslashes($_POST['stream_links_series']), true);
  $series_name = stripslashes($_POST['series_name']);
  save_serie_to_wordpress($series_name, $stream_links);
}

function save_serie_to_wordpress($serie_name, $stream_links_series) {
  $tv_shows_titles = get_post_type_titles('tvshows');
  $seasons_titles = get_post_type_titles('seasons');
  $episodes_titles = get_post_type_titles('episodes');
  $tmdb_id = get_uniquee_tmdb_id();

  $tv_show_has = tv_show_in_wp($tv_shows_titles, $serie_name);
  if (!$tv_show_has) {
    $post_id = wp_insert_post(array(
     	'post_type' => 'tvshows',
     	'post_title' => $serie_name,
     	'post_content' => $serie_name,
      'post_status' => 'publish'));
    add_post_meta($post_id, 'ids', $tmdb_id);
    add_post_meta($post_id, 'clgnrt', '1');

  }else {
    //if tv show has already in wordpress then get the tmdb id by follow algoritm:
    $query = new WP_Query([
      'title' => $serie_name,
      'post_type' => 'tvshows',
    ]);

    while ($query->have_posts()) {
      $query->the_post();
      //sometimes it can be array or just string
      $tmdb_id = is_array(get_post_meta(get_the_ID(), 'ids')) ? get_post_meta(get_the_ID(), 'ids')[0] : get_post_meta(get_the_ID(), 'ids');
    }
    wp_reset_postdata();
  }


  //$key is the number of season, $value - array that contains the streaming link for each episode in season
  foreach($stream_links_series as $season_num => $season_episodes) {
    $season_name = "$serie_name season $season_num";
 	  $has_season = season_in_wp($seasons_titles,$season_name);
    if (!$has_season) {
      $post_id = wp_insert_post(array(
     	 'post_type' => 'seasons',
     	 'post_title' => $season_name,
     	 'post_content' => $season_name,
       'post_status' => 'publish'));

      add_post_meta($post_id, 'ids', $tmdb_id);
      add_post_meta($post_id, 'serie', $serial_name);
      add_post_meta($post_id, 'temporada', (string) $season_num);
      add_post_meta($post_id, 'clgnrt', (string) $season_num);
    }

   foreach($season_episodes as $episode_num => $episode_streaming_links) {
	    $episode_num = (string) ((int) $episode_num + 1); // in the begin of loop episode_num = 0 change to 1
      $episode_name = "$serie_name season $season_num episode $episode_num";
      $has_ep = episode_in_wp($episodes_titles, $episode_name);
      if ($has_ep) continue;
      $post_id = wp_insert_post(array(
        'post_type' => 'episodes',
        'post_title' => $episode_name,
        'post_content' => $episode_name,
        'post_status' => 'publish'));

      $repeatable_fields = [];
      $i = 1;
      foreach($episode_streaming_links as $stream_link) {
        $repeatable_fields[] = ['name' => "Player $i", 'select' => 'iframe', 'idioma' => 'es', 'url' => $stream_link];
        $i++;
      }
     add_post_meta($post_id,'repeatable_fields', $repeatable_fields);
     add_post_meta($post_id, 'ids', $tmdb_id);
     add_post_meta($post_id, 'serie', (string) $serie_name);
     add_post_meta($post_id, 'episode_name', (string) $episode_name);
     add_post_meta($post_id, 'temporada', (string) $season_num);
     add_post_meta($post_id, 'clgnrt', $season_num);
     add_post_meta($post_id, 'episodio', (string) $episode_num);

   }
  }
}












function episode_in_wp($episodes_titles, $ep_title_add) {
  foreach ($episodes_titles as $ep_title) {
	if (strpos(str_replace(' ', '', strtolower($ep_title)),str_replace(' ', '', strtolower($ep_title_add))) !== false) return true;
  }
  return false;
}


#$season_title - name that script will add to wordpress
function season_in_wp($seasons_titles, $season_title_add) {
  foreach($seasons_titles as $season_title) {
    if (strpos(str_replace(' ', '', strtolower($season_title)),str_replace(' ', '', strtolower($season_title_add))) !== false) return true;
  }
  return false;
}

function tv_show_in_wp($tv_shows_titles,$serie_name) {
  foreach($tv_shows_titles as $tv_title) {
	if (strpos(str_replace(' ', '', strtolower($tv_title)),str_replace(' ', '', strtolower($serie_name))) !== false) return true;
  }
  return false;
}





//return all titles in post type
function get_post_type_titles($post_type) {
  $titles = [];

  $post_count = (int) wp_count_posts($post_type)->publish;
  for ($i=0;$i < ceil($post_count / 5000); $i++) {
    $query = new WP_Query([ 'post_type' => $post_type, 'offset' => ($i * 5000), 'posts_per_page' => 5000 ]);
    while ($query->have_posts()) {
      $query->the_post();
      $titles[] = get_the_title();
    }
    wp_reset_postdata();
  }

  return $titles;
}





//this function return the uniquee tmbd id
function get_uniquee_tmdb_id() {
 $tmdb_array = get_all_tmbd_in_wp();

 for($uniquee_id=1; $uniquee_id < 1000000000; $uniquee_id++) {
  $has_in_wp = false;
  foreach($tmdb_array as $tmdb_id) {
    if ($tmdb_id == $uniquee_id) {
	  $has_in_wp = true;
	  break;
	}
  }

  if ($has_in_wp) continue;
  return $uniquee_id;
 }
}



//this function get all tmbd from wordpress
function get_all_tmbd_in_wp() {
 $tmdbs = [];

 $post_count = (int) wp_count_posts('episodes')->publish;
 for ($i=0; $i < ceil($post_count / 5000); $i++) {
   $query = new WP_Query([ 'post_type' => 'episodes', 'offset' => ($i * 5000), 'posts_per_page' => 5000 ]);
   while ($query->have_posts()) {
     $query->the_post();
     $tmdbs[] = (int) get_post_meta(get_the_ID(), 'ids')[0];
   }
   wp_reset_postdata();
 }

 return $tmdbs;
}


 ?>
